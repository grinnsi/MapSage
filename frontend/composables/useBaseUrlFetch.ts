export const useBaseUrlFetch: typeof useFetch = (request, opts?) => {
  const config = useRuntimeConfig()
  
  return useFetch(request, { 
    baseURL: config.public.serverBaseURL,
    lazy: true,
    ...opts 
  })
}

export default useBaseUrlFetch