export enum UserRole {
    USER = 'user',
    CONTENT_MODERATOR = 'content_moderator',
    PLATFORM_ADMINISTRATOR = 'platform_administrator'
}

export interface AuthToken {
    access_token: string
    token_type: string
}

export interface LoginCredentials {
    username: string
    password: string
}

export interface SignupCredentials {
    email: string
    visible_name: string
    password: string
}

export interface UserPublic {
    visible_name: string
    user_role: UserRole
    enabled: boolean
    uuid: string
    created_at: string
    last_login: string | null
}

export interface AuthState {
    user: UserPublic | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean
} 