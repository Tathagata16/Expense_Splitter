import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { API_BASE_URL } from "../config/api";

function Home() {
  const navigate = useNavigate();

  const [groups, setGroups] = useState([]);

  const [newGroup, setNewGroup] = useState({
    group_name: "",
    description: "",
  });

  //storeing invitations
  const [invitations, setInvitations] = useState([]);
  //show or hide invitations
  const [showInvitations, setShowInvitations] =
    useState(false);

  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);


  useEffect(() => {
    const accessToken = localStorage.getItem("access");

    if (!accessToken) {
      navigate("/login");
    }

    fetchGroups();

    fetchInvitations();
  }, [navigate]);

  //fetching invitations
  async function fetchInvitations() {
    try {
      const accessToken = localStorage.getItem("access");

      const response = await fetch(
        `${API_BASE_URL}/api/groups/invitations/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();

        setInvitations(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  //function to fetch groups
  async function fetchGroups() {
    try {
      const accessToken = localStorage.getItem("access");

      const response = await fetch(
        `${API_BASE_URL}/api/groups/`,
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();

        setGroups(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  //function to create group
  async function handleCreateGroup() {
    if (!newGroup.group_name.trim()) {
      alert("Group name is required");

      return;
    }

    try {
      const accessToken = localStorage.getItem("access");

      const response = await fetch(
        `${API_BASE_URL}/api/groups/create/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },

          body: JSON.stringify({
            group_name: newGroup.group_name,
            group_type: "GROUP",
            description: newGroup.description,
          }),
        }
      );

      if (response.ok) {
        alert("Group created successfully");

        setNewGroup({
          group_name: "",
          description: "",
        });

        fetchGroups();
      } else {
        const errorData = await response.json();

        console.log(errorData);

        alert("Failed to create group");
      }
    } catch (error) {
      console.error(error);

      alert("Something went wrong");
    }
  }

  //handle invitation accept
  async function handleAcceptInvitation(
    invitationId
  ) {
    try {
      const accessToken =
        localStorage.getItem("access");

      const response = await fetch(
        `${API_BASE_URL}/api/groups/invitations/${invitationId}/accept/`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok) {
        alert("Invitation accepted!");

        fetchInvitations();

        fetchGroups();
      } else {
        const errorData =
          await response.json();

        console.log(errorData);

        alert(
          "Failed to accept invitation"
        );
      }
    } catch (error) {
      console.error(error);

      alert("Something went wrong");
    }
  }

  //handle invitation reject
  async function handleRejectInvitation(
    invitationId
  ) {
    try {
      const accessToken =
        localStorage.getItem("access");

      const response = await fetch(
        `${API_BASE_URL}/api/groups/invitations/${invitationId}/reject/`,
        {
          method: "POST",

          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      );

      if (response.ok) {
        alert("Invitation rejected!");

        fetchInvitations();
      } else {
        const errorData =
          await response.json();

        console.log(errorData);

        alert(
          "Failed to reject invitation"
        );
      }
    } catch (error) {
      console.error(error);

      alert("Something went wrong");
    }
  }

  //function to handle logout button
  async function handleLogout() {
    const refreshToken = localStorage.getItem("refresh");
    const accessToken = localStorage.getItem("access");

    try {
      await fetch(`${API_BASE_URL}/api/accounts/logout/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          refresh: refreshToken,
        }),
      });
    } catch (error) {
      console.error(error);
    }

    // Remove tokens regardless of API success
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    navigate("/login");
  }

  return (
    <div>
      <h1>Dashboard</h1>


      {/*creating new group */}
      <div
        style={{
          border: "1px solid black",
          padding: "10px",
          marginBottom: "20px",
        }}
      >
        <h3>Create Group</h3>

        <input
          type="text"
          placeholder="Group Name"
          value={newGroup.group_name}
          onChange={(e) =>
            setNewGroup({
              ...newGroup,
              group_name: e.target.value,
            })
          }
        />

        <br />
        <br />

        <textarea
          placeholder="Description"
          value={newGroup.description}
          onChange={(e) =>
            setNewGroup({
              ...newGroup,
              description: e.target.value,
            })
          }
        />

        <br />
        <br />

        <button onClick={handleCreateGroup}>
          Create Group
        </button>
      </div>


      {/*see invitations section */}
      <button
        onClick={() =>
          setShowInvitations(!showInvitations)
        }
      >
        Invitations ({invitations.length})
      </button>
      {showInvitations && (
        <div
          style={{
            border: "1px solid black",
            padding: "10px",
            marginTop: "10px",
            marginBottom: "20px",
          }}
        >
          <h3>Pending Invitations</h3>

          {invitations.length === 0 ? (
            <p>No pending invitations.</p>
          ) : (
            invitations.map((invitation) => (
              <div
                key={invitation.id}
                style={{
                  border: "1px solid gray",
                  padding: "10px",
                  marginBottom: "10px",
                }}
              >
                <p>
                  <strong>
                    {invitation.group_name}
                  </strong>
                </p>

                <p>
                  Invited by{" "}
                  {invitation.invited_by.username}
                </p>

                <button
                  onClick={() =>
                    handleAcceptInvitation(
                      invitation.id
                    )
                  }
                >
                  Accept
                </button>

                <button
                  style={{ marginLeft: "10px" }}
                  onClick={() =>
                    handleRejectInvitation(
                      invitation.id
                    )
                  }
                >
                  Reject
                </button>
              </div>
            ))
          )}
        </div>
      )}

      <h2>My Groups</h2>
      {/*to see existing group*/}
      {groups.length === 0 ? (
        <p>No groups yet.</p>
      ) : (
        groups.map((group) => (
          <div
            key={group.id}
            onClick={() => navigate(`/groups/${group.id}`)}
            style={{
              border: "1px solid black",
              padding: "10px",
              marginBottom: "10px",
              cursor: "pointer",
            }}
          >
            <h3>{group.group_name}</h3>

            <p>{group.description}</p>

            <p>
              Admin: {group.admin.username}
            </p>
          </div>
        ))
      )}

      <br />

      <button onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}

export default Home;