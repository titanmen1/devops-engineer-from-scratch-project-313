import { type DataProvider, fetchUtils, type Identifier } from "react-admin";

const apiUrl = import.meta.env.VITE_API_URL ?? "/api";

const httpClient = fetchUtils.fetchJson;

const collectionUrl = (resource: string) => `${apiUrl}/${resource}`;
const recordUrl = (resource: string, id: Identifier) =>
  `${collectionUrl(resource)}/${id}`;

/** Бэкенд отдаёт общее количество записей в заголовке `Content-Range: links 0-9/15` */
const parseTotal = (headers: Headers, fallback: number) => {
  const total = Number(headers.get("content-range")?.split("/").pop());
  return Number.isFinite(total) ? total : fallback;
};

/** Бэкенд ждёт диапазон в формате `[начало,конец)` */
const buildRangeQuery = (pagination?: { page: number; perPage: number }) => {
  const { page = 1, perPage = 10 } = pagination ?? {};
  const start = (page - 1) * perPage;
  return new URLSearchParams({
    range: JSON.stringify([start, start + perPage]),
  }).toString();
};

export const dataProvider: DataProvider = {
  getList: async (resource, params) => {
    const query = buildRangeQuery(params.pagination);
    const { headers, json } = await httpClient(
      `${collectionUrl(resource)}?${query}`,
    );
    return { data: json, total: parseTotal(headers, json.length) };
  },

  getOne: async (resource, params) => {
    const { json } = await httpClient(recordUrl(resource, params.id));
    return { data: json };
  },

  getMany: async (resource, params) => {
    const responses = await Promise.all(
      params.ids.map((id) => httpClient(recordUrl(resource, id))),
    );
    return { data: responses.map(({ json }) => json) };
  },

  getManyReference: async (resource, params) => {
    const query = buildRangeQuery(params.pagination);
    const { headers, json } = await httpClient(
      `${collectionUrl(resource)}?${query}`,
    );
    return { data: json, total: parseTotal(headers, json.length) };
  },

  create: async (resource, params) => {
    const { json } = await httpClient(collectionUrl(resource), {
      method: "POST",
      body: JSON.stringify(params.data),
    });
    return { data: json };
  },

  update: async (resource, params) => {
    const { json } = await httpClient(recordUrl(resource, params.id), {
      method: "PUT",
      body: JSON.stringify(params.data),
    });
    return { data: json };
  },

  updateMany: async (resource, params) => {
    await Promise.all(
      params.ids.map((id) =>
        httpClient(recordUrl(resource, id), {
          method: "PUT",
          body: JSON.stringify(params.data),
        }),
      ),
    );
    return { data: params.ids };
  },

  delete: async (resource, params) => {
    await httpClient(recordUrl(resource, params.id), { method: "DELETE" });
    return { data: params.previousData ?? { id: params.id } };
  },

  deleteMany: async (resource, params) => {
    await Promise.all(
      params.ids.map((id) =>
        httpClient(recordUrl(resource, id), { method: "DELETE" }),
      ),
    );
    return { data: params.ids };
  },
};
