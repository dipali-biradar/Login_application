import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import authService from "../services/authService";
import "../pages/AdminDashboard.css";

import Swal from "sweetalert2";

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const navigate = useNavigate();

  const [editUser, setEditUser] = useState(null);

  const [form, setForm] = useState({
    full_name: "",
    email: "",
    mobile: ""
  });

  const token = localStorage.getItem("token");

  // FETCH USERS
  const fetchUsers = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/admin/users", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUsers(res.data);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        navigate("/login");
      }
    }
  };

  // OPEN MODAL
  const openEditModal = (user) => {
    setEditUser(user);
    setForm({
      full_name: user.full_name,
      email: user.email,
      mobile: user.mobile
    });
  };

  // HANDLE INPUT CHANGE
  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // UPDATE USER
  const updateUser = async () => {
    const token = localStorage.getItem("token");

    try {
      await axios.put(
        `http://127.0.0.1:8000/admin/users/${editUser.id}`,
        form,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setEditUser(null);
      fetchUsers();
    } catch (err) {
      console.log(err.response?.data || err.message);
    }
  };

  // Deactive USER
const deactivateUser = async (id) => {
  try {
    await axios.patch(
      `http://127.0.0.1:8000/admin/users/${id}/deactivate`,
      {},
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    fetchUsers();

    Swal.fire({
      icon: "success",
      title: "Deactivated!",
      text: "User has been deactivated successfully.",
      timer: 1500,
      showConfirmButton: false,
    });

  } catch (error) {
    console.log(error.response?.data || error.message);
  }
};

const confirmDeactivate = async (id) => {
  const result = await Swal.fire({
    title: "Are you sure?",
    text: "Do you want to deactivate this user?",
    icon: "warning",
    showCancelButton: true,
    confirmButtonColor: "#d33",
    cancelButtonColor: "#3085d6",
    confirmButtonText: "Yes, Deactivate",
  });

  if (result.isConfirmed) {
    await deactivateUser(id);
  }
};
  useEffect(() => {
    fetchUsers();
  }, []);

  const logout = () => {
    authService.logout();
    localStorage.removeItem("user");
    localStorage.removeItem("token");
    navigate("/login");
  };
// Search & Pagination States
const [search, setSearch] = useState("");
const [currentPage, setCurrentPage] = useState(1);

const usersPerPage = 10;

// Filter Users
const filteredUsers = users.filter((user) =>
  user.full_name?.toLowerCase().includes(search.toLowerCase()) ||
  user.email?.toLowerCase().includes(search.toLowerCase())
);

// Pagination
const indexOfLastUser = currentPage * usersPerPage;
const indexOfFirstUser = indexOfLastUser - usersPerPage;

const currentUsers = filteredUsers.slice(
  indexOfFirstUser,
  indexOfLastUser
);

const totalPages =
  Math.ceil(filteredUsers.length / usersPerPage) || 1;
 

  return (
   <div className="dashboard-container">
  <div className="dashboard-header">
    <h1>Admin Dashboard</h1>

    <button className="logout-btn" onClick={logout}>
      Logout
    </button>
    <hr/>
  </div>
<div className="search-container">
  <input
    type="text"
    placeholder="Search by name or email..."
    value={search}
    onChange={(e) => {
      setSearch(e.target.value);
      setCurrentPage(1);
    }}
    className="search-input"
  />
</div>
  <div className="table-container">

      {/* TABLE */}
      <table border={1}>
        <thead>
          <tr>
            <th>Sr.no</th>
            <th>Name</th>
            <th>Email</th>
            <th>Mobile</th>
            <th>Role</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
       {currentUsers.map((u,index) => (
            <tr key={u.id}>
              <td>{indexOfFirstUser + index + 1}</td>
              <td>{u.full_name}</td>
              <td>{u.email}</td>
              <td>{u.mobile}</td>
               <td>{u.role}</td>
              <td>{u.status}</td>
              <td>
                {u.role !== "admin" && u.status === "active" && (
                  <>
                    <button  className="action-btn delete-btn" 
                    onClick={() => confirmDeactivate(u.id)}>
                      Deactive
                    </button>

                    <button   className="action-btn update-btn"
                     onClick={() => openEditModal(u)}>
                      Update
                    </button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
<div className="pagination">
  <button
    disabled={currentPage === 1}
    onClick={() =>
      setCurrentPage(currentPage - 1)
    }
  >
    Previous
  </button>

  <span>
    Page {currentPage} of {totalPages}
  </span>

  <button
    disabled={currentPage === totalPages}
    onClick={() =>
      setCurrentPage(currentPage + 1)
    }
  >
    Next
  </button>
</div>    
      {/* MODAL (IMPORTANT: INSIDE RETURN) */}
      {editUser && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h2>Edit User</h2>

            <input
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              placeholder="Full Name"
            />

            <input
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Email"
            />

            <input
              name="mobile"
              value={form.mobile}
              onChange={handleChange}
              placeholder="Mobile"
            />


            <div style={{ marginTop: "10px" }}>
              <button onClick={updateUser}>Save</button>
              <button onClick={() => setEditUser(null)}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

export default AdminDashboard;