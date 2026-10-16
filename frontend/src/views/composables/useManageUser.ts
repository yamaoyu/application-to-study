import { ref } from 'vue';
import { getUsersList, changeUserRole, changeUserStatus } from '../api/admin';
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

export const useChangeRole = () => {
    // ロールは2種類しかないので簡易的な実装で現在とは異なるロールに切り替える
    const changeRole = async (currentRole: UserRoleFilter, username: string) => {
        try {
            const nextRole = currentRole == "admin" ? "general" : "admin";
            await changeUserRole({ username: username, role: nextRole });
        } catch (error) {
            parseError(error, "ロール変更に失敗しました")
        }
    }

    return {
        changeRole
    }
}


export const useChangeStatus = () => {
    // ステータスは2種類しかないので簡易的な実装で現在とは異なるステータスに切り替える
    const changeStatus = async (currentStatus: UserStatusFilter, username: string) => {
        try {
            const nextStatus = currentStatus == "active" ? "suspended" : "active";
            await changeUserStatus({ username: username, status: nextStatus });
        } catch (error) {
            parseError(error, "ステータス変更に失敗しました")
        }
    }

    return {
        changeStatus
    }
}
