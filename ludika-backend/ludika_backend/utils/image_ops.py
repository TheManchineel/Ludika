import os
from uuid import uuid4
from PIL import Image
from sqlmodel import select, Session
from ludika_backend.models.games import GameImage

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "static")


def add_game_image_last(db_session: Session, game_id: int, file) -> str:
    """Add an image as the last image for a game."""
    last_image = db_session.exec(
        select(GameImage)
        .where(GameImage.game_id == game_id)
        .order_by(GameImage.position.desc())
    ).first()
    position = (last_image.position + 1) if last_image else 0
    img_uuid = str(uuid4()) + ".webp"
    out_path = os.path.join(STATIC_DIR, img_uuid)
    image = Image.open(file)
    if image.height > 500:
        ratio = 500 / image.height
        new_size = (int(image.width * ratio), 500)
        image = image.resize(new_size, Image.LANCZOS)
    image.save(out_path, "WEBP")
    new_img = GameImage(game_id=game_id, position=position, image=img_uuid)
    db_session.add(new_img)
    db_session.commit()
    return img_uuid


def overwrite_game_image(db_session: Session, game_id: int, position: int, file) -> str:
    """Replace an image at a given position for a game. Deletes the old file."""
    image_record = db_session.exec(
        select(GameImage).where(
            GameImage.game_id == game_id, GameImage.position == position
        )
    ).first()
    if not image_record:
        return None
    # Delete old file
    file_path = os.path.join(STATIC_DIR, image_record.image)
    if os.path.isfile(file_path):
        os.remove(file_path)
    # Save new file
    img_uuid = str(uuid4()) + ".webp"
    out_path = os.path.join(STATIC_DIR, img_uuid)
    image = Image.open(file)
    if image.height > 500:
        ratio = 500 / image.height
        new_size = (int(image.width * ratio), 500)
        image = image.resize(new_size, Image.LANCZOS)
    image.save(out_path, "WEBP")
    image_record.image = img_uuid
    db_session.commit()
    return img_uuid


def delete_image_from_game(db_session: Session, game_id: int, position: int) -> bool:
    """Delete an image at a given position for a game and remove the file."""
    image_record = db_session.exec(
        select(GameImage).where(
            GameImage.game_id == game_id, GameImage.position == position
        )
    ).first()
    if not image_record:
        return False
    file_path = os.path.join(STATIC_DIR, image_record.image)
    if os.path.isfile(file_path):
        os.remove(file_path)
    db_session.delete(image_record)
    db_session.commit()
    return True


def delete_all_game_images(db_session: Session, game_id: int) -> int:
    """Delete all images for a game and remove their files. Returns number deleted."""
    images = db_session.exec(
        select(GameImage).where(GameImage.game_id == game_id)
    ).all()
    count = 0
    for img in images:
        file_path = os.path.join(STATIC_DIR, img.image)
        if os.path.isfile(file_path):
            os.remove(file_path)
        db_session.delete(img)
        count += 1
    db_session.commit()
    return count
