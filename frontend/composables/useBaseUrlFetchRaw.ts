export const useBaseUrlFetchRaw: typeof $fetch.raw = (request, opts?) => {
  const config = useRuntimeConfig()
  
  return $fetch(request, { 
    baseURL: config.public.serverBaseURL, 
    lazy: true,
    ...opts 
  })
}

export default useBaseUrlFetchRaw