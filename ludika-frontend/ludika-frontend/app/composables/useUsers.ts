import type { UserPublic } from '../../types/auth'
import { useAuth } from './useAuth'

export const useUsers = () => {
    const users = ref<UserPublic[]>([])
    const user = ref<UserPublic | null>(null)
    const loading = ref(false)
    const userLoading = ref(false)
    const deleteLoading = ref(false)
    const error = ref<string | null>(null)
    const userError = ref<string | null>(null)
    const deleteError = ref<string | null>(null)

    const { authenticatedFetch, withSSRCheck } = useAuth()

    const _fetchUsers = async () => {
        loading.value = true
        error.value = null

        try {
            const response = await authenticatedFetch<UserPublic[]>('/api/v1/users/')
            users.value = response
        } catch (err) {
            error.value = 'Failed to fetch users'
            console.error('Error fetching users:', err)
        } finally {
            loading.value = false
        }
    }

    // SSR-safe version
    const fetchUsers = withSSRCheck(_fetchUsers)

    const _fetchUserById = async (uuid: string) => {
        userLoading.value = true
        userError.value = null

        try {
            const response = await authenticatedFetch<UserPublic>(`/api/v1/users/${uuid}`)
            user.value = response
        } catch (err) {
            userError.value = 'Failed to fetch user'
            console.error('Error fetching user:', err)
        } finally {
            userLoading.value = false
        }
    }

    // SSR-safe version
    const fetchUserById = withSSRCheck(_fetchUserById)

    const _fetchCurrentUser = async () => {
        userLoading.value = true
        userError.value = null

        try {
            const response = await authenticatedFetch<UserPublic>('/api/v1/users/me')
            user.value = response
        } catch (err) {
            userError.value = 'Failed to fetch current user'
            console.error('Error fetching current user:', err)
        } finally {
            userLoading.value = false
        }
    }

    // SSR-safe version
    const fetchCurrentUser = withSSRCheck(_fetchCurrentUser)

    const _deleteUser = async (uuid: string): Promise<void> => {
        deleteLoading.value = true
        deleteError.value = null

        try {
            await authenticatedFetch(`/api/v1/users/${uuid}`, {
                method: 'DELETE'
            })

            // Remove the user from the local users array
            users.value = users.value.filter(u => u.uuid !== uuid)
        } catch (err) {
            deleteError.value = 'Failed to delete user'
            console.error('Error deleting user:', err)
            throw err
        } finally {
            deleteLoading.value = false
        }
    }


    const _deleteUserGames = async (uuid: string): Promise<void> => {
        deleteLoading.value = true
        deleteError.value = null

        try {
            await authenticatedFetch(`/api/v1/users/${uuid}/games`, {
                method: 'DELETE'
            })
        } catch (err) {
            deleteError.value = 'Failed to delete user games'
            console.error('Error deleting user games:', err)
            throw err
        } finally {
            deleteLoading.value = false
        }
    }

    const _updateUser = async (uuid: string, updates: Partial<{ user_role: string; enabled: boolean }>): Promise<void> => {
        try {
            const response = await authenticatedFetch<UserPublic>(`/api/v1/users/${uuid}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(updates)
            })

            // Update the local user data if this is the currently loaded user
            if (user.value && user.value.uuid === uuid) {
                user.value = response
            }

            // Update the user in the users array if it exists
            const userIndex = users.value.findIndex(u => u.uuid === uuid)
            if (userIndex !== -1) {
                users.value[userIndex] = response
            }
        } catch (err) {
            console.error('Error updating user:', err)
            throw err
        }
    }

    const deleteUser = withSSRCheck(_deleteUser)
    const deleteUserGames = withSSRCheck(_deleteUserGames)
    const updateUser = withSSRCheck(_updateUser)

    return {
        users: readonly(users),
        user: readonly(user),
        loading: readonly(loading),
        userLoading: readonly(userLoading),
        deleteLoading: readonly(deleteLoading),
        error: readonly(error),
        userError: readonly(userError),
        deleteError: readonly(deleteError),
        fetchUsers,
        fetchUserById,
        fetchCurrentUser,
        deleteUser,
        updateUser,
        deleteUserGames
    }
}