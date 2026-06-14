import { BrowserRouter, Routes, Route } from "react-router-dom";
import GroupDetail from "./pages/GroupDetails";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />

        <Route path="/login" element={<Login />} />

        <Route path="/signup" element={<Signup />} />
        
        <Route path="/groups/:id" element={<GroupDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;