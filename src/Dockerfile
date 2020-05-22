FROM python:3.8.3-slim-buster

ENV APKTOOL_VERSION="2.4.1"
ENV ANDROID_HOME="/android-sdk-linux"
ENV BUILD_TOOLS_VERSION="29.0.3"
ENV PATH="${PATH}:${ANDROID_HOME}/tools/bin:${ANDROID_HOME}/build-tools/${BUILD_TOOLS_VERSION}"

# Install the needed tools.
RUN bash -c 'for i in {1..8}; do mkdir -p "/usr/share/man/man$i"; done' && \
    # Java JDK (needed for apktool and jarsigner).
    apt update && apt install --no-install-recommends -y openjdk-11-jdk-headless wget unzip && \
    # Android SDK (needed for zipalign).
    mkdir -p "${ANDROID_HOME}" && \
    wget -q "https://dl.google.com/android/repository/commandlinetools-linux-6200805_latest.zip" -O android-sdk.zip && \
    unzip -q android-sdk.zip -d "${ANDROID_HOME}" && rm android-sdk.zip && \
    yes | sdkmanager --sdk_root="${ANDROID_HOME}" "build-tools;${BUILD_TOOLS_VERSION}" && \
    # Apktool.
    wget -q "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool" \
    -O /usr/local/bin/apktool && chmod a+x /usr/local/bin/apktool && \
    wget -q "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_${APKTOOL_VERSION}.jar" \
    -O /usr/local/bin/apktool.jar && chmod a+x /usr/local/bin/apktool.jar && \
    # Clean.
    apt remove --purge -y wget unzip && \
    apt autoremove --purge -y && apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements and install.
COPY ./requirements.txt /Obfuscapk/
RUN python3 -m pip install --no-cache-dir -r /Obfuscapk/requirements.txt

# Copy the needed files.
COPY ./obfuscapk/ /Obfuscapk/obfuscapk/

# Set the working directory (to be used when mounting files from the host).
WORKDIR /workdir
VOLUME /workidr

# Set the entrypoint to Obfuscapk command line interface.
ENV PYTHONPATH="/Obfuscapk"

# Run with -u $(id -u):$(id -g) to avoid file permission issues.
ENTRYPOINT ["python3", "-m", "obfuscapk.cli"]
