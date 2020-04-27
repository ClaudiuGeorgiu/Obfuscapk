.class public Lcom/obfuscapk/demo/NativeLibraryDemo;
.super Ljava/lang/Object;
.source "NativeLibraryDemo.java"


# direct methods
.method static constructor <clinit>()V
    .locals 1

    const-string v0, "native-lib"

    .line 8
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private native stringFromJNI()Ljava/lang/String;
.end method


# virtual methods
.method public getMessageFromNativeLib()Ljava/lang/String;
    .locals 1

    .line 14
    invoke-direct {p0}, Lcom/obfuscapk/demo/NativeLibraryDemo;->stringFromJNI()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method
