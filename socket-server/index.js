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
    methods: ["GET", "POST"],
    allowedHeaders: [
      "Authorization",
      "Content-Type",
      "ApplicationKey",
      "Authorization",
    ],
  },
});
io.use(async (socket, next) => {
  const headers = socket.handshake.headers;
  const query = socket.handshake.query;
  const clientKey = headers["applicationkey"] || query.ApplicationKey;
  const clientToken = headers["authorization"] || query.Authorization;
  if (clientKey === "@OAIIA3UHUIE21vczx@faWOOCS)=123SAF") return next();
  if (clientKey && clientToken) {
    try {
      const userdata = await axios.get(
        "http://localhost:5001/api/user_socket/",
        {
          headers: {
            ApplicationKey: clientKey,
            Authorization: clientToken,
          },
        }
      );
      socket.user = {
        ...userdata,
        ApplicationKey: clientKey,
      };
      return next();
    } catch (e) {
      console.log(e);
    }
  } else {
    return new Error("Unauthorized: Invalid key or token");
  }
});
io.on("connection", (socket) => {
  const user = socket.user;
  if (user?.ApplicationKey && user?.data?.info) {
    if (!connected_list[user?.ApplicationKey])
      connected_list[user?.ApplicationKey] = [];
    connected_list[user?.ApplicationKey].push({
      id: socket.id,
      user: user?.data.info,
      staff__id: user?.data?.id,
    });
    socket.join(`user_${user?.ApplicationKey}`);
    socket.to(`user_${user?.ApplicationKey}`).emit("message", {
      type: "userEvent",
      action: "connect",
      data: {
        id: socket.id,
        user: user?.data.info,
      },
    });
    io.emit("online_users", connected_list[user?.ApplicationKey]);
  }
  socket.on("message", (msg_data) => {
    if (user?.ApplicationKey) {
      if (msg_data?.type == "user") {
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
        data.key;
      }
      if (msg_data?.type == "group") {
        // Gửi cho cá nhân
      }
    }
  });
  socket.on("backend_event", (data) => {
    if (data?.type === "chat_message") {
      // Nếu mà gửi tin nhắn message bằng backend
      // Lấy danh sách người nhận
      const to = data?.room?.members.filter(
        (staff) => staff.id !== data.data.sender
      );
      // Kiểm tra người dùng có online không
      if (connected_list[data.key]) {
        for (let i = 0; i < to.length; i++) {
          const online = connected_list[data.key].find(
            (user) => user?.staff__id === to[i].id
          );
          if (online) {
            socket.to(online.id).emit("message", {
              type: "message",
              user: user?.data?.profile,
              data: data?.data,
            });
            console.log("List user:", connected_list[data.key]);
            console.log("Sended to:", online?.user?.profile?.username);
          } else {
            console.log("Người dùng offline!");
          }
        }
      }
    }
  });
  socket.on("disconnect", () => {
    if (user?.ApplicationKey && user?.data?.info) {
      connected_list[user?.ApplicationKey] = connected_list[
        user?.ApplicationKey
      ].filter((user) => user.id !== socket.id);
      socket.to(`user_${user?.ApplicationKey}`).emit("message", {
        type: "userEvent",
        action: "dissconnect",
        data: {
          id: socket.id,
          user: user?.data?.info,
        },
      });
    }
    console.log(`❌ Client disconnected: ${socket.id}`);
  });
});
server.listen(5000, () => {
  console.log("🚀 Socket.IO server running at http://0.0.0.0:5000");
});
