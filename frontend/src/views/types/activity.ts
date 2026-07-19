export type OneActivity = {
    activity_id: number;
    date: string;
    target_time: number;
    actual_time: number;
    status: string;
};

export type SendTargetActivityParam = {
    date: string,
    target_time: number
}

type RegisterTargetErrorReason =
    | "TARGET_TIME_ALREADY_REGISTERED"
    | "SALARY_NOT_FOUND"
    | "UNEXPECTED_ERROR";


export type registerTargetResult =
    | {
        result: "success";
        date: string;
        target_time: number;
        reason: null;
    }
    | {
        result: "error";
        date: string;
        target_time: null;
        reason: RegisterTargetErrorReason;
    };

export type RegisterTargetResponse = {
    results: registerTargetResult[]
}

export type SendActualActivityParam = {
    date: string,
    actual_time: number
}

type RegisterActualErrorReason =
    | "ACTIVITY_NOT_FOUND"
    | "ACTIVITY_ALREADY_FINISHED"
    | "SALARY_NOT_FOUND"
    | "UNEXPECTED_ERROR";

export type RegisterActualResult =
    | {
        result: "success";
        date: string;
        actual_time: number;
        reason: null;
    }
    | {
        result: "error";
        date: string;
        actual_time: null;
        reason: RegisterActualErrorReason;
    };

export type RegisterActualResponse = {
    results: RegisterActualResult[]
}

export type SendFinishActivityParam = string[]

export type FinishActivityErrorReason =
    | "ACTIVITY_NOT_FOUND"
    | "ACTIVITY_ALREADY_FINISHED"
    | "SALARY_NOT_FOUND"
    | "UNEXPECTED_ERROR";

type finishDetail =
    | {
        "date": string,
        "reason": null,
        "result": "success",
        "bonus": number,
        "penalty": number,
        "status": "success" | "error"
    }
    | {
        "date": string,
        "reason": FinishActivityErrorReason,
        "result": "error",
        "bonus": null,
        "penalty": null,
        "status": null
    }


export type FinishActivityResponse = {
    "pay_adjustment": number,
    "total_bonus": number,
    "total_penalty": number,
    "results": finishDetail[]
}


export type GetOneActivityResponse = {
    activity_id: number,
    date: string,
    target_time: number,
    actual_time: number,
    status: "success" | "failure" | "pending",
    bonus: number,
    penalty: number
}

type ActivitySummary = {
    totalincome: number;
    salary: number;
    pay_adjustment: number;
    bonus: number;
    penalty: number;
    success_days: number;
    fail_days: number;
};

export type GetAllActivitiesResponse = ActivitySummary;

type MonthlyActivity = {
    date: string;
    target_time: number;
    actual_time: number;
    status: "pending" | "success" | "failure",
    bonus: number,
    penalty: number
};

export type GetActivitiesByMonthResponse = ActivitySummary & {
    activity_list: MonthlyActivity[];
};

// 年ごとの情報取得時の各月の情報
type YearlyMonthlyInfo = {
    month: number;
    total_income: number;
    salary: number;
    pay_adjustment: number;
    bonus: number;
    penalty: number;
    success_days: number;
    fail_days: number;
};

export type GetActivitiesByYearResponse = ActivitySummary & {
    monthly_info: YearlyMonthlyInfo[];
};
