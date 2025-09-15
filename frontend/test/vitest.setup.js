import { vi } from 'vitest';
import { createPinia } from 'pinia';
import { mount } from '@vue/test-utils'


// モックのルーターを作成
vi.mock('vue-router', async () => {
    const actual = await vi.importActual('vue-router')
    return {
        ...actual,
        useRoute: () => ({
            query: {}
        }),
        useRouter: () => ({
            push: vi.fn()
        })
    }
})

// モックのaxiosを作成
vi.mock("axios")

export const mountComponent = (component) => {
    return mount(component, {
        global: {
            plugins: [createPinia()],
        },
    })
}