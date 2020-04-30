.class public Lcom/obfuscapk/demo/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 11
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method


# virtual methods
.method public synthetic lambda$onCreate$0$MainActivity(Landroid/widget/EditText;Landroid/view/View;)V
    .locals 1

    .line 22
    invoke-virtual {p1}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    const-string p2, "Obfuscapk"

    .line 23
    invoke-virtual {p2, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    const/4 p2, 0x0

    if-eqz p1, :cond_0

    .line 24
    invoke-virtual {p0}, Lcom/obfuscapk/demo/MainActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object p1

    const-string v0, "Correct password!"

    invoke-static {p1, v0, p2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object p1

    invoke-virtual {p1}, Landroid/widget/Toast;->show()V

    goto :goto_0

    .line 26
    :cond_0
    invoke-virtual {p0}, Lcom/obfuscapk/demo/MainActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object p1

    const-string v0, "Wrong password!"

    invoke-static {p1, v0, p2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object p1

    invoke-virtual {p1}, Landroid/widget/Toast;->show()V

    :goto_0
    return-void
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .locals 3

    const-string v0, "Obfuscapk"

    .line 15
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    const/high16 p1, 0x7f040000

    .line 16
    invoke-virtual {p0, p1}, Lcom/obfuscapk/demo/MainActivity;->setContentView(I)V

    const/high16 p1, 0x7f030000

    .line 18
    invoke-virtual {p0, p1}, Lcom/obfuscapk/demo/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object p1

    check-cast p1, Landroid/widget/Button;

    const v1, 0x7f030001

    .line 19
    invoke-virtual {p0, v1}, Lcom/obfuscapk/demo/MainActivity;->findViewById(I)Landroid/view/View;

    move-result-object v1

    check-cast v1, Landroid/widget/EditText;

    .line 21
    new-instance v2, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;

    invoke-direct {v2, p0, v1}, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;-><init>(Lcom/obfuscapk/demo/MainActivity;Landroid/widget/EditText;)V

    invoke-virtual {p1, v2}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 31
    :try_start_0
    new-instance p1, Lcom/obfuscapk/demo/AssetDemo;

    invoke-direct {p1}, Lcom/obfuscapk/demo/AssetDemo;-><init>()V

    const-string v1, "ASSET TEST"

    .line 32
    invoke-virtual {p0}, Lcom/obfuscapk/demo/MainActivity;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v2

    invoke-virtual {p1, v2}, Lcom/obfuscapk/demo/AssetDemo;->getMessageFromAsset(Landroid/content/res/AssetManager;)Ljava/lang/String;

    move-result-object p1

    invoke-static {v1, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const-string p1, "DEBUG INFO TEST"

    .line 34
    invoke-static {v0}, Lcom/obfuscapk/demo/DebugInfoDemo;->getDebugMessage(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p1, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const-string p1, "GOTO TEST"

    .line 36
    invoke-static {}, Lcom/obfuscapk/demo/OrderDemo;->getGotoMessage()Ljava/lang/String;

    move-result-object v1

    invoke-static {p1, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 38
    new-instance p1, Lcom/obfuscapk/demo/NativeLibraryDemo;

    invoke-direct {p1}, Lcom/obfuscapk/demo/NativeLibraryDemo;-><init>()V

    const-string v1, "NATIVE LIB TEST"

    .line 39
    invoke-virtual {p1}, Lcom/obfuscapk/demo/NativeLibraryDemo;->getMessageFromNativeLib()Ljava/lang/String;

    move-result-object p1

    invoke-static {v1, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const-string p1, "NOP TEST"

    .line 41
    invoke-static {v0}, Lcom/obfuscapk/demo/NopDemo;->getNopMessage(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-static {p1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const-string p1, "REORDER TEST"

    .line 43
    invoke-static {}, Lcom/obfuscapk/demo/OrderDemo;->getGotoMessage()Ljava/lang/String;

    move-result-object v0

    invoke-static {p1, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    :catch_0
    move-exception p1

    .line 45
    invoke-virtual {p0}, Lcom/obfuscapk/demo/MainActivity;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    invoke-virtual {p1}, Ljava/lang/Exception;->toString()Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x0

    invoke-static {v0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 46
    invoke-virtual {p1}, Ljava/lang/Exception;->toString()Ljava/lang/String;

    move-result-object p1

    const-string v0, "MAIN ERROR"

    invoke-static {v0, p1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    :goto_0
    return-void
.end method
