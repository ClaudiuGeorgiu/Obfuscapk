FROM python:3.7.4-slim-stretch

ENV APKTOOL_VERSION="2.4.0"
ENV ANDROID_HOME="/android-sdk-linux"
ENV BUILD_TOOLS_VERSION="29.0.2"
ENV PATH="${PATH}:${ANDROID_HOME}/tools/bin:${ANDROID_HOME}/build-tools/${BUILD_TOOLS_VERSION}"

# Install the needed tools.
RUN bash -c 'for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done' && \
    # Java 8 (needed for apktool and jarsigner).
    apt update && apt install --no-install-recommends -y openjdk-8-jdk-headless wget unzip && \
    # Android SDK (needed for zipalign).
    mkdir -p "${ANDROID_HOME}" && \
    wget -q "https://dl.google.com/android/repository/sdk-tools-linux-4333796.zip" && \
    unzip -q sdk-tools-linux-4333796.zip -d "${ANDROID_HOME}" && \
    rm sdk-tools-linux-4333796.zip && \
    yes | sdkmanager "build-tools;${BUILD_TOOLS_VERSION}" && \
    # Apktool.
    wget -q "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool" \
    -O /usr/local/bin/apktool && chmod a+x /usr/local/bin/apktool && \
    wget -q "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_${APKTOOL_VERSION}.jar" \
    -O /usr/local/bin/apktool.jar && chmod a+x /usr/local/bin/apktool.jar && \
    # Clean.
    apt remove --purge -y wget unzip && \
    apt autoremove --purge -y && apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy the source code.
COPY . /Obfuscapk

# Install Python requirements.
RUN python3.7 -m pip install --no-cache-dir -r /Obfuscapk/requirements.txt

# Set the working directory (to be used when mounting files from the host).
WORKDIR /workdir
VOLUME /workidr

# Set the entrypoint to Obfuscapk command line interface.
ENV PYTHONPATH="/Obfuscapk"
ENTRYPOINT ["python3.7", "-m", "obfuscapk.cli"]
