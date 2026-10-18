import { ref, type Ref } from 'vue';
import { getUsersList, changeUserRole, changeUserStatus, resetUserPassword } from '../api/admin';
import { parseError } from '../utils/error';
import { UserItem, UserStatusFilter, UserRoleFilter, ResetPasswordResponse } from '../types/admin';

export const useGetUsersList = (message: Ref<string>, isSuccess: Ref<boolean>) => {
    const users = ref<UserItem[]>([]);
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
            users.value = res.data.users;
            isSuccess.value = true;
        } catch (error) {
            message.value = parseError(error, "ユーザー一覧の取得に失敗しました");
            isSuccess.value = false;
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

export const useChangeRole = (message: Ref<string>, isSuccess: Ref<boolean>) => {
    // ロールは2種類しかないので簡易的な実装で現在とは異なるロールに切り替える
    const changeRole = async (currentRole: UserRoleFilter, username: string) => {
        try {
            const nextRole = currentRole == "admin" ? "general" : "admin";
            await changeUserRole({ username: username, role: nextRole });
            isSuccess.value = true;
        } catch (error) {
            message.value = parseError(error, "ロール変更に失敗しました");
            isSuccess.value = false;
        }
    }

    return {
        changeRole
    }
}


export const useChangeStatus = (message: Ref<string>, isSuccess: Ref<boolean>) => {
    // ステータスは2種類しかないので簡易的な実装で現在とは異なるステータスに切り替える
    const changeStatus = async (currentStatus: UserStatusFilter, username: string) => {
        try {
            const nextStatus = currentStatus == "active" ? "suspended" : "active";
            await changeUserStatus({ username: username, status: nextStatus });
            isSuccess.value = true;
        } catch (error) {
            message.value = parseError(error, "ステータス変更に失敗しました");
            isSuccess.value = false;
        }
    }

    return {
        changeStatus
    }
}

export const useResetPassword = (message: Ref<string>, isSuccess: Ref<boolean>) => {
    const makeMessage = (passwordInfo: ResetPasswordResponse) => {
        const messages: Array<string> = ["パスワードリセットに成功しました", "この情報は一度しか表示されません"];
        messages.push(`ユーザー名: ${passwordInfo.username}`);
        messages.push(`新しいパスワード: ${passwordInfo.password}`);
        return messages.join("\n");
    }
    const resetPassword = async (username: string) => {
        try {
            const res = await resetUserPassword(username);
            message.value = makeMessage(res.data);
            isSuccess.value = true;
        } catch (error) {
            message.value = parseError(error, "パスワードリセットに失敗しました");
            isSuccess.value = false;
        }
    }

    return {
        resetPassword
    }
}
