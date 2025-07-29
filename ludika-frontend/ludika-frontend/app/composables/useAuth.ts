import type { AuthToken, LoginCredentials, UserPublic, AuthState } from '../../types/auth'

const AUTH_TOKEN_KEY = 'ludika_auth_token'

export const useAuth = () => {
    const state = reactive<AuthState>({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false
    })

    // Initialize auth state from localStorage on client side
    const initializeAuth = () => {
        if (process.client) {
            const storedToken = localStorage.getItem(AUTH_TOKEN_KEY)
            if (storedToken) {
                state.token = storedToken
                state.isAuthenticated = true
                // Fetch user info if we have a token
                getCurrentUser()
            }
        }
    }

    // Login function
    const login = async (credentials: LoginCredentials): Promise<void> => {
        state.isLoading = true

        try {
            // Create form data as required by the backend
            const formData = new FormData()
            formData.append('username', credentials.username)
            formData.append('password', credentials.password)

            const response = await $fetch<AuthToken>('/api/v1/auth/login', {
                method: 'POST',
                body: formData
            })

            // Store token
            state.token = response.access_token
            state.isAuthenticated = true

            if (process.client) {
                localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
            }

            // Fetch user info
            await getCurrentUser()
        } catch (error) {
            state.token = null
            state.isAuthenticated = false
            state.user = null

            if (process.client) {
                localStorage.removeItem(AUTH_TOKEN_KEY)
            }

            throw error
        } finally {
            state.isLoading = false
        }
    }

    // Logout function
    const logout = () => {
        state.token = null
        state.user = null
        state.isAuthenticated = false

        if (process.client) {
            localStorage.removeItem(AUTH_TOKEN_KEY)
        }
    }

    // Get current user info
    const getCurrentUser = async (): Promise<void> => {
        if (!state.token) return

        try {
            const user = await $fetch<UserPublic>('/api/v1/users/me', {
                headers: {
                    Authorization: `Bearer ${state.token}`
                }
            })

            state.user = user
        } catch (error) {
            // Token might be invalid, logout
            logout()
            throw error
        }
    }

    // Create authenticated fetch wrapper
    const authenticatedFetch = async <T>(url: string, options: any = {}): Promise<T> => {
        const headers = {
            ...options.headers,
            ...(state.token && { Authorization: `Bearer ${state.token}` })
        }

        return $fetch<T>(url, {
            ...options,
            headers
        })
    }

    // Check if user has specific role
    const hasRole = (role: string): boolean => {
        return state.user?.user_role === role
    }

    // Check if user is admin
    const isAdmin = (): boolean => {
        return hasRole('platform_administrator')
    }

    return {
        // State (readonly)
        user: readonly(toRef(state, 'user')),
        token: readonly(toRef(state, 'token')),
        isAuthenticated: readonly(toRef(state, 'isAuthenticated')),
        isLoading: readonly(toRef(state, 'isLoading')),

        // Methods
        login,
        logout,
        getCurrentUser,
        initializeAuth,
        authenticatedFetch,
        hasRole,
        isAdmin
    }
} 