const { default: axios } = require("axios");
const express = require("express");
const http = require("http");
const { Server } = require("socket.io");

// Khởi tạo app
const app = express();
const server = http.createServer(app);
const connected_list = [];
const io = new Server(server, {
  cors: {
    origin: "*", // chỉ cho localhost
    // origin: ["http://localhost", "http://localhost:3000"], // chỉ cho localhost
    // methods: ["GET", "POST"]
  },
});
// Middleware xác thực header khi client connect
io.use(async (socket, next) => {
  const headers = socket.handshake.headers;
  const clientKey = headers["applicationkey"];
  const clientToken = headers["authorization"];
  if (clientKey === "@OAIIA3UHUIE21vczx@faWOOCS)=123SAF") return next();
  if (clientKey && clientToken) {
    try {
      const userdata = await axios.get("http://localhost:8000/api/user/", {
        headers: {
          ApplicationKey: clientKey,
          Authorization: clientToken,
        },
      });
      socket.user = { ...userdata, ApplicationKey: clientKey };
      return next();
    } catch (e) {
      console.log(e);
    }
  } else {
    return next(new Error("Unauthorized: Invalid key or token"));
  }
});
io.on("connection", (socket) => {
  const user = socket.user;
  if (user?.ApplicationKey && user?.data?.profile) {
    console.log(user?.data?.profile.full_name, socket.id);
    if (!connected_list[user?.ApplicationKey])
      connected_list[user?.ApplicationKey] = [];
    connected_list[user?.ApplicationKey].push({
      id: socket.id,
      user: user?.data?.profile,
    });
    socket.join(`user_${user?.ApplicationKey}`);
    socket.to(`user_${user?.ApplicationKey}`).emit("message", {
      type: "userEvent",
      action: "connect",
      data: {
        id: socket.id,
        user: user?.data?.profile,
      },
    });
    io.emit("online_users", connected_list[user?.ApplicationKey]);
  }
  socket.on("message", (msg_data) => {
    if (user?.ApplicationKey) {
      // socket.to(`user_${user?.ApplicationKey}`).emit("message", {
      //   type: "message",
      //   user: user?.data?.profile,
      //   data: msg_data,
      // });
      if (msg_data?.type == "user") {
        // Gửi cho cá nhân với id là staff id
        const online = connected_list[user?.ApplicationKey].filter(
          (user) => user?.user?.id === msg_data?.to
        );
        online.forEach((userItem) => {
          if (userItem.id) {
            // Nếu người dùng online
            console.log("Gửi cho cá nhân!", userItem?.id);
            socket.to(userItem.id).emit("message", {
              type: "message",
              user: user?.data?.profile,
              data: msg_data,
            });
          }
        });
      }
      if (msg_data?.type == "group") {
        // Gửi cho cá nhân
      }
    }
  });
  socket.on("backend_event", (data) => {
    if (data?.ApplicationKey) {
      socket.to(`user_${data?.ApplicationKey}`).emit("message", data.data);
    }
  });
  socket.on("disconnect", () => {
    if (user?.ApplicationKey && user?.data?.profile) {
      connected_list[user?.ApplicationKey] = connected_list[
        user?.ApplicationKey
      ].filter((user) => user?.id !== socket.id);
      socket.to(`user_${user?.ApplicationKey}`).emit("message", {
        type: "userEvent",
        action: "dissconnect",
        data: {
          id: socket.id,
          user: user?.data?.profile,
        },
      });
    }
    console.log(`❌ Client disconnected: ${socket.id}`);
  });
});
server.listen(5000, () => {
  console.log("🚀 Socket.IO server running at http://0.0.0.0:5000");
});
