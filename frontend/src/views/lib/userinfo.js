export function validateUsername(username) {
    const validate = () => {
        // ユーザー名が3文字以上16文字以下かどうかを判定
        if (username.value === '') {
            return null
        }
        return username.value.length >= 3 && username.value.length <= 16}
    
    return {
        validate
    }
}

export function validatePassword(password) {
    const validate = () => {
        // パスワードが条件を満たしているかどうかを判定
        if (password.value === '') {
            // パスワードが未入力の場合は対象外
            return { valid:null, message: '' }
        }

        const hasLowercase = /[a-z]/;
        const hasUppercase = /[A-Z]/;
        const hasNumber = /\d/;
        const hasSpecialChar = /[!@#$%&*()+\-=[\]{};:<>,./?_~|]/;

        if (password.value.length < 8 || password.value.length > 16){
            return { valid:false, message: 'パスワードは8文字以上16文字以下にして下さい' }
        } else if (!hasLowercase.test(password.value)){
            return { valid:false, message: '小文字が含まれていません' }
        } else if (!hasUppercase.test(password.value)){
            return { valid:false, message: '大文字が含まれていません' }
        } else if (!hasNumber.test(password.value)){
            return { valid:false, message: '数字が含まれていません' }
        } else if (!hasSpecialChar.test(password.value)){
            return { valid:false, message: '記号が含まれていません' }
        } else {
            return { valid:true, message: 'OK' }
        }
    }

    return {
        validate
    }
}

export function checkPassword(password, passwordCheck){
    const validate = () => {
        // 入力された2つパスワードが一致しているかどうかを判定
        if (passwordCheck.value === '') {
            return null
        }
        return password.value === passwordCheck.value
    }

    return {
        validate
    }
}

export function validateEmail(email) {
    const validate = () => {
        // メールアドレスの形式かどうかを判定
        if (email.value === '') {
            return null
        }
        const emailPattern = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
        return emailPattern.test(email.value);
    }

    return {
        validate
    }
}