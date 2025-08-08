import type { AuthToken, LoginCredentials, SignupCredentials, UserPublic, AuthState } from '../../types/auth'
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

    const signup = async (credentials: SignupCredentials): Promise<void> => {
        globalState.isLoading = true

        try {
            const formData = new FormData()
            formData.append('email', credentials.email)
            formData.append('visible_name', credentials.visible_name)
            formData.append('password', credentials.password)

            await $fetch('/api/v1/auth/signup', {
                method: 'POST',
                body: formData
            })

            // After successful signup, automatically log in (could be done prettier but ehh)
            await login({
                username: credentials.email,
                password: credentials.password
            })
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
        if (import.meta.client && !globalState.token) {
            initializeAuth()
        }

        const headers = {
            ...options.headers,
            ...(globalState.token && { Authorization: `Bearer ${globalState.token}` })
        }

        try {
            return await $fetch<T>(url, {
                ...options,
                headers
            })
        } catch (error: any) {
            if (error?.status === 401 || error?.statusCode === 401) {
                console.log('401 error detected, logging out and retrying without auth')

                logout()

                try {
                    const headersWithoutAuth = { ...options.headers }
                    return await $fetch<T>(url, {
                        ...options,
                        headers: headersWithoutAuth
                    })
                } catch (retryError: any) {
                    console.log('Retry without auth also failed, redirecting to login')

                    if (import.meta.client) {
                        await navigateTo('/login')
                    }

                    throw retryError
                }
            }

            throw error
        }
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

    const isPrivileged = (): boolean => {
        return isAdmin() || isContentModerator()
    }

    const canEditGame = (game: any): boolean => {
        if (!globalState.user) return false

        // Privileged users can edit any game
        if (isPrivileged()) {
            return true
        }

        // Regular users can edit their own games if they're in draft status
        if (game.proposing_user === globalState.user.uuid && game.status === 'draft') {
            return true
        }

        return false
    }

    // SSR-aware wrapper for any async function that needs authentication
    const withSSRCheck = <T extends (...args: any[]) => Promise<any>>(fn: T): T => {
        return ((...args: any[]) => {
            if (!import.meta.client) {
                return Promise.resolve()
            }
            return fn(...args)
        }) as T
    }

    return {
        user: readonly(toRef(globalState, 'user')),
        token: readonly(toRef(globalState, 'token')),
        isAuthenticated: readonly(toRef(globalState, 'isAuthenticated')),
        isLoading: readonly(toRef(globalState, 'isLoading')),

        login,
        signup,
        logout,
        getCurrentUser,
        initializeAuth,
        authenticatedFetch,
        withSSRCheck,
        hasRole,
        isAdmin,
        isContentModerator,
        isUser,
        isPrivileged,
        canEditGame
    }
} 