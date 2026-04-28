import { vi } from 'vitest';
import { createPinia } from 'pinia';
import { mount, type MountingOptions } from '@vue/test-utils'
import type { Component } from 'vue';

export const mockRouterPush = vi.fn();

// モックのルーターを作成
vi.mock('vue-router', async () => {
    const actual = await vi.importActual('vue-router')
    return {
        ...actual,
        useRoute: () => ({
            query: {}
        }),
        useRouter: () => ({
            push: mockRouterPush
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

export const mountComponent = (
    component: Component,
    options: MountingOptions<any> = {}) => {
    return mount(component, {
        global: {
            plugins: [createPinia()],
        },
        ...options
    })
}