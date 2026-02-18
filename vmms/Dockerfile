# Autolab - autograding docker image

FROM ubuntu:22.04
MAINTAINER Autolab Team <autolab-dev@andrew.cmu.edu>

RUN apt-get update && apt-get install -y \
  build-essential \
  vim \
  gcc \
  git \
  cmake \
  make \
  sudo \
  python3 \
  python3-pip \
  python3-venv \
  && rm -rf /var/lib/apt/lists/*

# Install autodriver
WORKDIR /home
RUN useradd autolab
RUN useradd autograde
RUN mkdir autolab autograde output
RUN chown autolab:autolab autolab
RUN chown autolab:autolab output
RUN chown autograde:autograde autograde
RUN git clone --depth 1 https://github.com/autolab/Tango.git
WORKDIR Tango/autodriver
RUN make clean && make
RUN cp autodriver /usr/bin/autodriver
RUN chmod +s /usr/bin/autodriver

# Clean up
WORKDIR /home
RUN apt-get -y autoremove && rm -rf Tango/

# Check installation
RUN ls -l /home
RUN which autodriver


# Newly Added #
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        build-essential wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Install OpenCilk into /opt/opencilk
RUN mkdir -p /opt/opencilk && \
    wget https://github.com/OpenCilk/opencilk-project/releases/download/opencilk/v2.1/opencilk-2.1.0-x86_64-linux-gnu-ubuntu-22.04.sh -O /tmp/opencilk.sh && \
    sh /tmp/opencilk.sh --prefix=/opt/opencilk --exclude-subdir && \
    rm /tmp/opencilk.sh

# Put OpenCilk's clang/clang++ first on PATH for all users
ENV PATH=/opt/opencilk/bin:${PATH}

# Install Cheetah for opencilk
# Clone cheetah at the requested branch
RUN git clone --branch opencilk/v2.1 https://github.com/OpenCilk/cheetah.git

# Comment out the -mavx line in cheetah/runtime/CMakeLists.txt
RUN sed -i 's/^ *list(APPEND CHEETAH_COMPILE_FLAGS -mavx)/# &/' \
    cheetah/runtime/CMakeLists.txt

# Configure and build cheetah
RUN mkdir -p cheetah/build && cd cheetah/build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_C_COMPILER=/opt/opencilk/bin/clang \
          -DCMAKE_CXX_COMPILER=/opt/opencilk/bin/clang++ \
          -DLLVM_CMAKE_DIR=/opt/opencilk \
          ../ && \
    cmake --build .
