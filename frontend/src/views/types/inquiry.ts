export const INQUIRY_CATEGORIES = ["要望", "エラー報告", "その他"] as const;
export type InquiryCategoryType = typeof INQUIRY_CATEGORIES[number];
export const DEFAULT_INQUIRY_CATEGORY: InquiryCategoryType = "要望";

export type CreateInquiryResponse = {
    "category": InquiryCategoryType
    "detail": string
}

export type GetInquiryInfo = CreateInquiryResponse & {
    "date": string
    "is_checked": boolean
}