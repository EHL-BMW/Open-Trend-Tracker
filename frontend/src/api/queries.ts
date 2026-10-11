import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./endpoints";
import type { AnalysisRequest } from "./types";

export const queryKeys = {
  catalog: ["catalog"] as const,
  runs: (limit: number) => ["runs", limit] as const,
  run: (id: string) => ["run", id] as const,
};

export const RUN_HISTORY_LIMIT = 20;

export function useCatalog() {
  return useQuery({
    queryKey: queryKeys.catalog,
    queryFn: ({ signal }) => api.getCatalog(signal),
    staleTime: 5 * 60_000,
  });
}

export function useRunHistory() {
  return useQuery({
    queryKey: queryKeys.runs(RUN_HISTORY_LIMIT),
    queryFn: ({ signal }) => api.listRuns(RUN_HISTORY_LIMIT, signal),
  });
}

export function useRunAnalysis() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AnalysisRequest) => api.runAnalysis(body),
    onSuccess: (run) => {
      queryClient.setQueryData(queryKeys.run(run.id), run);
      void queryClient.invalidateQueries({ queryKey: ["runs"] });
    },
  });
}

export function useOpenRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      queryClient.fetchQuery({
        queryKey: queryKeys.run(id),
        queryFn: ({ signal }) => api.getRun(id, signal),
        staleTime: Infinity,
      }),
  });
}
