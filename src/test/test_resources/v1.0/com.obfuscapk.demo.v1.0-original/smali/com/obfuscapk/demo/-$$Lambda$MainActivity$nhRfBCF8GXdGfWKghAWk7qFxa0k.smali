.class public final synthetic Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;
.super Ljava/lang/Object;
.source "lambda"

# interfaces
.implements Landroid/view/View$OnClickListener;


# instance fields
.field private final synthetic f$0:Lcom/obfuscapk/demo/MainActivity;

.field private final synthetic f$1:Landroid/widget/EditText;


# direct methods
.method public synthetic constructor <init>(Lcom/obfuscapk/demo/MainActivity;Landroid/widget/EditText;)V
    .locals 0

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;->f$0:Lcom/obfuscapk/demo/MainActivity;

    iput-object p2, p0, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;->f$1:Landroid/widget/EditText;

    return-void
.end method


# virtual methods
.method public final onClick(Landroid/view/View;)V
    .locals 2

    iget-object v0, p0, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;->f$0:Lcom/obfuscapk/demo/MainActivity;

    iget-object v1, p0, Lcom/obfuscapk/demo/-$$Lambda$MainActivity$nhRfBCF8GXdGfWKghAWk7qFxa0k;->f$1:Landroid/widget/EditText;

    invoke-virtual {v0, v1, p1}, Lcom/obfuscapk/demo/MainActivity;->lambda$onCreate$0$MainActivity(Landroid/widget/EditText;Landroid/view/View;)V

    return-void
.end method
