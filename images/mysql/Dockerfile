# =======================
# 1. Build Stage
# =======================
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    git cmake gcc g++ make bzip2 pkg-config \
    libncurses5-dev libssl-dev libaio-dev libtirpc-dev libzstd-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Source code will be copied here by build.py
COPY source/ /build/source/

RUN mkdir build && \
    cd build && \
    cmake ../source \
        -DDOWNLOAD_BOOST=1 \
        -DWITH_BOOST=../boost \
        -DCMAKE_INSTALL_PREFIX=/usr/local/mysql && \
    make -j"$(nproc)" && \
    make install DESTDIR=/opt/mysql


# =======================
# 2. Runtime Stage
# =======================
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    libaio1 libncurses5 openssl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy compiled binaries
COPY --from=builder /opt/mysql/ /opt/mysql/

# Create MySQL directories
RUN mkdir -p /opt/mysql/data && \
    chmod -R 755 /opt/mysql && \
    chown -R 1001:1001 /opt/mysql

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

USER 1001

EXPOSE 3306

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/opt/mysql/usr/local/mysql/bin/mysqld"]