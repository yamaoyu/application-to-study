export const INQUIRY_CATEGORIES = ["要望", "エラー報告", "その他"] as const;
export type InquiryCategoryType = typeof INQUIRY_CATEGORIES[number];
export const DEFAULT_INQUIRY_CATEGORY: InquiryCategoryType = "要望";

export type CreateInquiryResponse = {
    "category": InquiryCategoryType
    "detail": string
}

type InquiryPriority = "高" | "中" | "低";

export type InquiryItem = {
    id: number
    detail: string
    date: Date
    category: InquiryCategoryType
    priority: InquiryPriority | null
    is_checked: boolean | null
}

export type GetInquiryInfo = {
    inquiries: InquiryItem[]
}