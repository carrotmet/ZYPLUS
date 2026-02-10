# 使用Nginx作为基础镜像来提供静态文件服务
FROM nginx:alpine

# 设置工作目录
WORKDIR /usr/share/nginx/html

# 删除默认的Nginx网站文件
RUN rm -rf /usr/share/nginx/html/*

# 复制网站文件到镜像中
COPY . /usr/share/nginx/html/

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露80端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]