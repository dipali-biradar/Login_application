import api from "./axios";

export const getUsers = async () => {
  const response = await api.get(
    "/admin/users"
  );

  return response;
};

export const updateUser = async (
  userId,
  data
) => {
  return await api.put(
    `/admin/users/${userId}`,
    data
  );
};

export const deactivateUser = async (
  userId
) => {
  return await api.patch(
    `/admin/users/${userId}/deactivate`
  );
};

export const activateUser = async (
  userId
) => {
  return await api.patch(
    `/admin/users/${userId}/activate`
  );
};
