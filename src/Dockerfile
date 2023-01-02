FROM python:3.11.1-slim-bullseye

ENV APKTOOL_VERSION="2.7.0"
ENV ANDROID_HOME="/android-sdk-linux"
ENV BUILD_TOOLS_VERSION="33.0.0"
ENV PATH="${PATH}:${ANDROID_HOME}/tools/bin:${ANDROID_HOME}/cmdline-tools/bin:${ANDROID_HOME}/build-tools/${BUILD_TOOLS_VERSION}"

# Install the needed tools.
RUN apt update && \
    # Java JDK (needed for apktool).
    apt install --no-install-recommends -y openjdk-11-jdk-headless wget unzip && \
    # Android SDK (needed for zipalign and apksigner).
    mkdir -p "${ANDROID_HOME}" && \
    wget -q "https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip" -O android-sdk.zip && \
    unzip -q android-sdk.zip -d "${ANDROID_HOME}" && rm android-sdk.zip && \
    yes | sdkmanager --sdk_root="${ANDROID_HOME}" "build-tools;${BUILD_TOOLS_VERSION}" && \
    # Apktool.
    wget -q "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool" \
    -O /usr/local/bin/apktool && chmod a+x /usr/local/bin/apktool && \
    wget -q "https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_${APKTOOL_VERSION}.jar" \
    -O /usr/local/bin/apktool.jar && chmod a+x /usr/local/bin/apktool.jar && \
    # BundleDecompiler.
    wget -q "https://raw.githubusercontent.com/TamilanPeriyasamy/BundleDecompiler/master/build/libs/BundleDecompiler-0.0.2.jar" \
    -O /usr/local/bin/BundleDecompiler.jar && chmod a+x /usr/local/bin/BundleDecompiler.jar && \
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
VOLUME /workdir

# Set the entrypoint to Obfuscapk command line interface.
ENV PYTHONPATH="/Obfuscapk"

# Run with -u $(id -u):$(id -g) to avoid file permission issues.
ENTRYPOINT ["python3", "-m", "obfuscapk.cli"]
