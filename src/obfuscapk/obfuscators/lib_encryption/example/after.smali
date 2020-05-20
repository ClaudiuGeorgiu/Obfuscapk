.class public Lcom/obfuscapk/demo/NativeLibraryDemo;
.super Ljava/lang/Object;
.source "NativeLibraryDemo.java"


# direct methods
.method static constructor <clinit>()V
    .locals 2

    .prologue
    .line 8
    const-string/jumbo v0, "native-lib"

    const-class v1, Lcom/obfuscapk/demo/NativeLibraryDemo;

    invoke-static {v1, v0}, Lcom/decryptassetmanager/DecryptAsset;->loadEncryptedLibrary(Ljava/lang/Class;Ljava/lang/String;)V

    .line 9
    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .prologue
    .line 3
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private native stringFromJNI()Ljava/lang/String;
.end method


# virtual methods
.method public getMessageFromNativeLib()Ljava/lang/String;
    .locals 1

    .prologue
    .line 14
    invoke-direct {p0}, Lcom/obfuscapk/demo/NativeLibraryDemo;->stringFromJNI()Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method
