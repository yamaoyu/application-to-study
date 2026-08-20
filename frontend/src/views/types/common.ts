export type BulkResponse<T> = {
    success_count: number
    error_count: number
    results: T[]
}
