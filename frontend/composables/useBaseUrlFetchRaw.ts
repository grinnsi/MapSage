export const useBaseUrlFetchRaw: typeof $fetch.raw = (request, opts?) => {
  const config = useRuntimeConfig()
  
  return $fetch.raw(request, { baseURL: config.public.baseURL, ...opts })
}

export default useBaseUrlFetchRaw