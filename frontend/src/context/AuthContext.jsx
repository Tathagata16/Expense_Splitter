import {
    createContext,
    useContext,
    useEffect,
    useState,
} from "react";

const AuthContext = createContext();

export function AuthProvider({
    children,
}) {
    const [user, setUser] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    useEffect(() => {
        fetchCurrentUser();
    }, []);

    async function fetchCurrentUser() {
        const access =
            localStorage.getItem(
                "access"
            );

        if (!access) {
            setLoading(false);

            return;
        }

        try {
            const response =
                await fetch(
                    "http://127.0.0.1:8000/api/accounts/me/",
                    {
                        headers: {
                            Authorization:
                                `Bearer ${access}`,
                        },
                    }
                );

            if (response.ok) {
                const data =
                    await response.json();

                setUser(data);
            }
        } catch (error) {
            console.error(error);
        }

        setLoading(false);
    }

    return (
        <AuthContext.Provider
            value={{
                user,
                loading,
                fetchCurrentUser,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(
        AuthContext
    );
}










