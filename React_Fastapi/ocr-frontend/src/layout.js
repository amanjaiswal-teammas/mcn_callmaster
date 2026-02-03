import React, { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import topLogo from "./assets/logo.png";
import accountLogo from "./assets/account.png";
import { BASE_URL } from "./components/config";
import {
  House,
  Settings,
  LogOut,
  Captions,
  AudioLines,
  Terminal,
  FileKey,
  ChartNoAxesCombined,
  ChevronDown,
  ChevronRight,
  Search,
  DollarSign,
  EyeOff,
  Phone,
  Boxes,
} from "lucide-react";

const iconMap = {
  House,
  Settings,
  LogOut,
  Captions,
  AudioLines,
  Terminal,
  FileKey,
  ChartNoAxesCombined,
  Search,
  DollarSign,
  EyeOff,
  Phone,
  Calling: Phone,
  Boxes,
};

const Layout = ({ onLogout, children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [username, setUsername] = useState("");
  const [menuItems, setMenuItems] = useState([]);
  const [openMenus, setOpenMenus] = useState(
    JSON.parse(localStorage.getItem("openMenus")) || { Service: false, Sales: false,Collection:false }
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedName = localStorage.getItem("username");
    setUsername(storedName ? storedName.split(" ")[0] : "");
  }, []);

//  useEffect(() => {
//    const fetchMenu = async () => {
//      try {
//        setLoading(true);
//        const response = await fetch(`${BASE_URL}/menu`);
//        if (!response.ok) throw new Error("Failed to fetch menu");
//        const data = await response.json();
//
//        const filteredMenu = data.filter(item => {
//        if ([22, 37].includes(userId)) {
//          return ["Home", "Service", "Logout"].includes(item.name);
//        }
//        return true; // all items for other users
//      });
//
//        const formattedMenu = data
//          .filter((item) =>
//            ["Home", "Recordings", "Transcription", "Prompt", "Settings", "API Key", "User Access","Calling","Collection", "Service", "Sales"].includes(item.name)
//          )
//          .map((item) => ({
//            ...item,
//            Icon: iconMap[item.icon] || null,
//            url: item.url?.trim(),
//            submenu: item.submenu || [],
//          }));
//
//        setMenuItems(formattedMenu);
//      } catch (error) {
//        console.error("Failed to fetch menu:", error);
//      } finally {
//        setLoading(false);
//      }
//    };
//
//    fetchMenu();
//  }, []);

useEffect(() => {
  const fetchMenu = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/menu`);
      if (!response.ok) throw new Error("Failed to fetch menu");

      const data = await response.json();


        const userId = Number(localStorage.getItem("id"));

        const allowedNames = userId === 37
          ? ["Home", "Service", "Logout"]
          : [
              "Home",
//              "Recordings",
//              "Transcription",
//              "Prompt",
//              "Settings",
//              "API Key",
//              "User Access",
              "Calling",
              "Collection",
              "Service",
              "Sales"
            ];



      const formattedMenu = data
        .filter(item => allowedNames.includes(item.name))
        .map(item => ({
          ...item,
          Icon: iconMap[item.icon] || null,
          url: item.url?.trim(),
          submenu: item.submenu || [],
        }));

      setMenuItems(formattedMenu);
    } catch (error) {
      console.error("Failed to fetch menu:", error);
    } finally {
      setLoading(false);
    }
  };

  fetchMenu();
}, []);


  useEffect(() => {
    localStorage.setItem("openMenus", JSON.stringify(openMenus));
  }, [openMenus]);

  const toggleMenu = (menu) => {
    setOpenMenus((prev) => {
      const newState = { ...prev, [menu]: !prev[menu] };
      localStorage.setItem("openMenus", JSON.stringify(newState));
      return newState;
    });
  };

  const handleNavigation = (path, menu) => {
    navigate(path);
    if (menu) {
      setOpenMenus((prev) => {
        const newState = { ...prev, [menu]: true };
        localStorage.setItem("openMenus", JSON.stringify(newState));
        return newState;
      });
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("isLoggedIn");
    localStorage.removeItem("openMenus");
    sessionStorage.removeItem("user");

    if (onLogout) onLogout();

    setTimeout(() => {
      window.location.href = "/";
    }, 100);
  };

  return (
    <div className="dashboard-layout5">
      <div className="top-navbar">
        <img src={topLogo} alt="Company Logo" className="top-logo" />
        <div className="top-text">
          <p>Your Transcription & Analysis Hub!</p>
        </div>
        <div className="account">
          <img src={accountLogo} alt="loginname" className="account-logo" />
          <span>{username}</span>
        </div>
      </div>

      <div className="content-layout5">
        <div className="sidebar5">
          {loading ? (
            <p>Loading menu...</p>
          ) : (
            menuItems.map(({ url, name, Icon, submenu }) => (
              <div key={name}>
                <button
                  className={`nav-button ${location.pathname === url ? "active" : ""}`}
                  title={submenu.length ? `Expand ${name} menu` : `Go to ${name}`}
                  onClick={() => (submenu.length ? toggleMenu(name) : handleNavigation(url))}
                >
                  {Icon && <Icon size={20} className="icon" />} {name}
                  {submenu.length > 0 &&
                    (openMenus[name] ? <ChevronDown size={16} /> : <ChevronRight size={16} />)}
                </button>

                {submenu.length > 0 && openMenus[name] && (
                  <div className="submenu">
                    {submenu.map(({ url, name, Icon }) => (
                      <button
                        key={url}
                        className={`sub-nav-button ${location.pathname === url ? "active" : ""}`}
                        title={`Go to ${name}`}
                        onClick={() => handleNavigation(url, name)}
                      >
                        {Icon && <Icon size={16} className="icon" />} {name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}

          <button
            className="nav-button logout-button"
            title="Log out of your account"
            onClick={handleLogout}
          >
            <LogOut size={20} className="icon" /> Logout
          </button>
        </div>

        <div className="main-content">{children}</div>
      </div>
    </div>
  );
};

export default Layout;
