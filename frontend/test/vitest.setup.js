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
vi.mock('@/views/api/client', () => ({
  apiClient: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}))

export const mountComponent = (component, options = {}) => {
    return mount(component, {
        global: {
            plugins: [createPinia()],
        },
        ...options
    })
}