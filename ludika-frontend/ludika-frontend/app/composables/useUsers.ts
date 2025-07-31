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

    // SSR-safe version
    const deleteUser = withSSRCheck(_deleteUser)

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
        deleteUser
    }
}