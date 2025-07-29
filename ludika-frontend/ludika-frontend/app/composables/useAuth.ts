import type { AuthToken, LoginCredentials, UserPublic, AuthState } from '../../types/auth'
import { UserRole } from '../../types/auth'

const AUTH_TOKEN_KEY = 'ludika_auth_token'

export const getUserRoleDisplayName = (role: UserRole): string => {
    switch (role) {
        case UserRole.USER:
            return 'User'
        case UserRole.CONTENT_MODERATOR:
            return 'Content Moderator'
        case UserRole.PLATFORM_ADMINISTRATOR:
            return 'Platform Administrator'
        default:
            return 'Unknown Role'
    }
}

// Global state that will be shared across all useAuth() calls
const globalState = reactive<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false
})

export const useAuth = () => {
    const initializeAuth = () => {
        if (import.meta.client) {
            const storedToken = localStorage.getItem(AUTH_TOKEN_KEY)
            console.log('Stored token:', storedToken)
            if (storedToken) {
                globalState.token = storedToken
                globalState.isAuthenticated = true
                getCurrentUser()
            }
        }
    }

    const login = async (credentials: LoginCredentials): Promise<void> => {
        globalState.isLoading = true

        try {
            const formData = new FormData()
            formData.append('username', credentials.username)
            formData.append('password', credentials.password)

            const response = await $fetch<AuthToken>('/api/v1/auth/login', {
                method: 'POST',
                body: formData
            })

            globalState.token = response.access_token
            globalState.isAuthenticated = true

            if (import.meta.client) {
                localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
            }

            await getCurrentUser()
        } catch (error) {
            console.log(error)
            globalState.token = null
            globalState.isAuthenticated = false
            globalState.user = null

            if (import.meta.client) {
                localStorage.removeItem(AUTH_TOKEN_KEY)
            }

            throw error
        } finally {
            globalState.isLoading = false
        }
    }

    const logout = () => {
        globalState.token = null
        globalState.user = null
        globalState.isAuthenticated = false

        if (import.meta.client) {
            localStorage.removeItem(AUTH_TOKEN_KEY)
        }
    }

    const getCurrentUser = async (): Promise<void> => {
        if (!globalState.token) return

        try {
            const user = await $fetch<UserPublic>('/api/v1/users/me', {
                headers: {
                    Authorization: `Bearer ${globalState.token}`
                }
            })

            globalState.user = user
        } catch (error) {
            // Token might be invalid, logout
            logout()
            throw error
        }
    }

    const authenticatedFetch = async <T>(url: string, options: any = {}): Promise<T> => {
        const headers = {
            ...options.headers,
            ...(globalState.token && { Authorization: `Bearer ${globalState.token}` })
        }

        return $fetch<T>(url, {
            ...options,
            headers
        })
    }

    const hasRole = (role: UserRole): boolean => {
        return globalState.user?.user_role === role
    }

    const isAdmin = (): boolean => {
        return hasRole(UserRole.PLATFORM_ADMINISTRATOR)
    }

    const isContentModerator = (): boolean => {
        return hasRole(UserRole.CONTENT_MODERATOR)
    }

    const isUser = (): boolean => {
        return hasRole(UserRole.USER)
    }

    return {
        user: readonly(toRef(globalState, 'user')),
        token: readonly(toRef(globalState, 'token')),
        isAuthenticated: readonly(toRef(globalState, 'isAuthenticated')),
        isLoading: readonly(toRef(globalState, 'isLoading')),

        login,
        logout,
        getCurrentUser,
        initializeAuth,
        authenticatedFetch,
        hasRole,
        isAdmin,
        isContentModerator,
        isUser
    }
} 