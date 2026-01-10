
import { ApiClient } from './api-client'

// Mock the global fetch function
global.fetch = jest.fn()

describe('ApiClient', () => {
    let apiClient: ApiClient

    beforeEach(() => {
        // Reset mocks and environment before each test
        jest.clearAllMocks()
        process.env.NEXT_PUBLIC_USE_MOCK_DATA = 'false'
        process.env.NEXT_PUBLIC_API_URL = 'http://api.example.com'
        apiClient = new ApiClient(process.env.NEXT_PUBLIC_API_URL!)
    })

    describe('Environment Configuration', () => {
        it('should use mock data when NEXT_PUBLIC_USE_MOCK_DATA is true', async () => {
            process.env.NEXT_PUBLIC_USE_MOCK_DATA = 'true'
            const client = new ApiClient('http://api.example.com')

            // Spy on console.log to verify mock path
            const consoleSpy = jest.spyOn(console, 'log').mockImplementation()

            // Making a call that has a mock handler
            await (client as any).fetch('/it-staff/alerts')

            // fetch should NOT be called because it returns mock data directly
            expect(global.fetch).not.toHaveBeenCalled()

            // Should verify it hit the mock log
            expect(consoleSpy).toHaveBeenCalledWith(expect.stringContaining('[Mock API] Serving request'))

            consoleSpy.mockRestore()
        })

        it('should use real API when NEXT_PUBLIC_USE_MOCK_DATA is false', async () => {
            process.env.NEXT_PUBLIC_USE_MOCK_DATA = 'false'
            const client = new ApiClient('http://api.example.com');

            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => ({})
            })

            await (client as any).fetch('/test')

            expect(global.fetch).toHaveBeenCalled()
        })
    })

    describe('Headers', () => {
        it('should include Content-Type header by default', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => ({})
            })

            const client = new ApiClient('http://api.example.com')
            await (client as any).fetch('/test')

            expect(global.fetch).toHaveBeenCalledWith(
                'http://api.example.com/test',
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Content-Type': 'application/json'
                    })
                })
            )
        })

        it('should include Authorization header when token is set', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => ({})
            })

            const client = new ApiClient('http://api.example.com')
            client.setToken('fake-token')
            await (client as any).fetch('/test')

            expect(global.fetch).toHaveBeenCalledWith(
                'http://api.example.com/test',
                expect.objectContaining({
                    headers: expect.objectContaining({
                        'Authorization': 'Bearer fake-token'
                    })
                })
            )
        })
    })

    describe('Error Handling', () => {
        it('should throw error on non-ok response', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: false,
                status: 500,
                statusText: 'Internal Server Error'
            })

            // Make sure we are not in mock mode
            process.env.NEXT_PUBLIC_USE_MOCK_DATA = 'false'
            const client = new ApiClient('http://api.example.com')

            await expect((client as any).fetch('/test')).rejects.toThrow('API Error: 500 Internal Server Error')
        })
    })

    describe('Specific Methods', () => {
        it('getExecutiveDashboard should call correct endpoint', async () => {
            (global.fetch as jest.Mock).mockResolvedValueOnce({
                ok: true,
                json: async () => ({})
            })

            // Make sure we are not in mock mode
            process.env.NEXT_PUBLIC_USE_MOCK_DATA = 'false'
            const client = new ApiClient('http://api.example.com')

            await client.getExecutiveDashboard('tenant-1')

            expect(global.fetch).toHaveBeenCalledWith(
                'http://api.example.com/tenant-1/executive/dashboard',
                expect.any(Object)
            )
        })
    })
})
