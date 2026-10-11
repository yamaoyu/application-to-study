import { ref } from 'vue';
import { getUsersList } from '../api/admin';
import { parseError } from '../utils/error';
import { UserItem, UserStatusFilter, UserRoleFilter } from '../types/admin';

export const useGetUsersList = () => {
    const users = ref<UserItem[]>([]);
    const message = ref<string>("");
    const userStatus = ref<UserStatusFilter>("");
    const userRole = ref<UserRoleFilter>("")
    const lastActiveAt = ref<string>("")
    const createdAt = ref<string>("")
    const username = ref<string>("")

    const makeParams = () => ({
        status: userStatus.value || undefined,
        last_active_at: lastActiveAt.value || undefined,
        created_at: createdAt.value || undefined,
        role: userRole.value || undefined,
        username: username.value || undefined
    });

    const getUsers = async () => {
        try {
            const res = await getUsersList(makeParams());
            users.value = res.data.users
        } catch (error) {
            message.value = parseError(error, "ユーザー一覧の取得に失敗しました");
        }
    }

    return {
        getUsers,
        users,
        userStatus,
        userRole,
        lastActiveAt,
        createdAt,
        username,
        message
    }
}
