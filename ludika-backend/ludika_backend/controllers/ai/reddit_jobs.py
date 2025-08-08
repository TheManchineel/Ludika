import json
from threading import Thread, Lock

from langchain_core.runnables import RunnableLambda

from sqlmodel import select

from ludika_backend.controllers.ai.agents import game_detection_executor, DetectionResult, \
    create_agent_executor_for_game_create
from ludika_backend.controllers.scraping.reddit import get_top_posts, RedditPost
from ludika_backend.models import Game
from ludika_backend.utils.counter import AtomicCounter
from ludika_backend.utils.db import get_session, db_context
from ludika_backend.utils.logs import get_logger


job_lock = Lock()

class RedditJob:
    """This class represents a job for background scraping and processing of Reddit posts. Unashamedly a singleton."""
    def __init__(self):
        self._thread = None
        self._posts_found = 0
        self._posts_processed_counter = AtomicCounter()
        self._games_found_counter = AtomicCounter()
        self._games_added_counter = AtomicCounter()


    def pipeline_factory(self):
        """Create a pipeline for processing Reddit posts, binding it to the current instance."""
        def detect_and_process(post: RedditPost):
            raw_detection = game_detection_executor.invoke(
                {"post_content": f"{post.title}{'\n\n' + post.url if post.url else ''}\n\n{post.selftext}"}
            )

            detection = DetectionResult(**json.loads(raw_detection["output"]))
            self._posts_processed_counter.increment()

            if detection.has_game_url and detection.url:
                self._games_found_counter.increment()
                get_logger().info(f"Found game URL: {detection.url} for post: {post.title}")
                with db_context() as db_session:
                    if db_session.exec(select(Game).where(Game.url == detection.url)).first():
                        return {"skipped": True, "reason": "Game already exists", "post_title": post.title}
                executor = create_agent_executor_for_game_create(detection.url, game_added_callback=lambda: self._games_added_counter.increment())
                return executor.invoke({})

            return {"skipped": True, "reason": "No game URL detected", "post_title": post.title}

        def complete_pipeline():
            self._posts = get_top_posts()
            self._posts_found = len(self._posts)
            RunnableLambda(detect_and_process).batch(self._posts)

        return complete_pipeline

    def is_running(self):
        return self._thread and self._thread.is_alive()

    def start(self):
        """Start the pipeline."""
        if not self.is_running():
            pipeline = self.pipeline_factory()
            self._thread = Thread(target=pipeline, args=())
            self._games_found_counter.reset()
            self._games_added_counter.reset()
            self._posts_processed_counter.reset()
            self._thread.start()
            return True
        return False

    def get_stats(self):
        return {
            "status": "running" if self.is_running() else "stopped",
            "posts_found": self._posts_found,
            "posts_processed": self._posts_processed_counter.get_value(),
            "games_found": self._games_found_counter.get_value(),
            "games_added": self._games_added_counter.get_value(),
        }

CURRENT_JOB = RedditJob()

def get_job_stats():
    with job_lock:
        return CURRENT_JOB.get_stats()

def start_job():
    with job_lock:
        return CURRENT_JOB.start()