export type ActivityStatus =
    | "pending"
    | "success"
    | "failure"

export type SendTargetActivityParam = {
    date: string,
    target_time: number
}

export type RegisterTargetErrorReason =
    | "TARGET_TIME_ALREADY_REGISTERED"
    | "SALARY_NOT_FOUND"
    | "UNEXPECTED_ERROR";


export type RegisterTargetResult =
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
    results: RegisterTargetResult[]
}

export type SendActualActivityParam = {
    date: string,
    actual_time: number
}

export type RegisterActualErrorReason =
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

type FinishDetail =
    | {
        "date": string,
        "reason": null,
        "result": "success",
        "bonus": number,
        "penalty": number,
        "status": ActivityStatus
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
    "results": FinishDetail[]
}

export type OneActivity = {
    activity_id: number;
    date: string;
    target_time: number;
    actual_time: number;
    status: ActivityStatus;
    bonus: number,
    penalty: number
};

export type GetOneActivityResponse = OneActivity

export type GetActivitiesByStatus = {
    activities: OneActivity[]
}

export type ActivitySummary = {
    total_income: number;
    salary: number;
    pay_adjustment: number;
    bonus: number;
    penalty: number;
    success_days: number;
    fail_days: number;
};

export type GetAllActivitiesResponse = ActivitySummary;

export type MonthlyActivity = {
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
export type YearlyMonthlyInfo = {
    month: number;
    total_income: number;
    salary: number;
    pay_adjustment: number;
    bonus: number;
    penalty: number;
    success_days: number;
    fail_days: number;
};

export type MonthKey =
    | "jan" | "feb" | "mar" | "apr"
    | "may" | "jun" | "jul" | "aug"
    | "sep" | "oct" | "nov" | "dec";

export type GetActivitiesByYearResponse = ActivitySummary & {
    monthly_info: Record<MonthKey, Partial<YearlyMonthlyInfo>>;
};
