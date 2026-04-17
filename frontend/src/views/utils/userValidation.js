export const validateUsername = (username) => {
  if (!username) {
    return { valid: null, message: '' }
  }
  if (username.length < 3 || username.length > 16) {
    return { valid: false, message : 'ユーザー名は3文字以上16文字以下にして下さい' };
  }
  return { valid: true, message: '' };
};

export const validatePassword = (password) => {
    // パスワードが条件を満たしているかどうかを判定
    if (!password) {
        // パスワードが未入力の場合は対象外
        return { valid:null, message: '' }
    };

    const hasLowercase = /[a-z]/;
    const hasUppercase = /[A-Z]/;
    const hasNumber = /\d/;
    const hasSpecialChar = /[!@#$%&*()+\-=[\]{};:<>,./?_~|]/;

    if (password.length < 8 || password.length > 16){
        return { valid:false, message: 'パスワードは8文字以上16文字以下にして下さい' }
    } else if (!hasLowercase.test(password)){
        return { valid:false, message: '小文字が含まれていません' }
    } else if (!hasUppercase.test(password)){
        return { valid:false, message: '大文字が含まれていません' }
    } else if (!hasNumber.test(password)){
        return { valid:false, message: '数字が含まれていません' }
    } else if (!hasSpecialChar.test(password)){
        return { valid:false, message: '記号が含まれていません' }
    } else {
        return { valid:true, message: 'OK' }
    }
};

export const checkPassword = (password, passwordCheck) => {
  if (!passwordCheck) {
    return { valid: null, message: '' }
  };

  if (password !== passwordCheck) {
    return { valid: false, message: 'パスワードが一致しません' }
  };

  return { valid: true, message: '' };
};

export const validateEmail = (email) => {
    // メールアドレスの形式かどうかを判定
    if (!email) {
        return { valid: null, message: '' }
    };
    const emailPattern = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
    const valid = emailPattern.test(email);
    if (valid) {
      return { valid: valid, message: '' }
    };

    return { valid: valid, message: 'メールアドレスの形式で入力して下さい' };
};
