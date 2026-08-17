from html import escape

from app.core.config import Settings

BRAND = "#0f3d2e"
BRAND_INK = "#1a1a1a"
MUTED = "#5c5a55"
SURFACE = "#ffffff"
PAGE_BG = "#f7f6f3"
ACCENT_URGENTE = "#b54708"
FONT_SANS = "Arial,Helvetica,sans-serif"
FONT_SERIF = "Georgia,'Times New Roman',serif"


def _cta(label: str, url: str) -> str:
    safe_url = escape(url, quote=True)
    safe_label = escape(label)
    return (
        '<table role="presentation" cellspacing="0" cellpadding="0"><tr>'
        f'<td style="background:{BRAND};border-radius:4px;">'
        f'<a href="{safe_url}" style="display:inline-block;padding:12px 22px;'
        f"color:{PAGE_BG};text-decoration:none;font-weight:600;font-size:15px;"
        f'font-family:{FONT_SERIF};">{safe_label}</a>'
        "</td></tr></table>"
    )


def render_layout(
    *,
    preheader: str,
    eyebrow: str,
    heading: str,
    body_html: str,
    cta_label: str,
    cta_url: str,
    note: str,
    footer: str,
    accent: str = BRAND,
) -> str:
    return f"""\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>{escape(heading)}</title>
</head>
<body style="margin:0;padding:0;background:{PAGE_BG};">
  <div style="display:none;max-height:0;overflow:hidden;opacity:0;">
    {escape(preheader)}
  </div>
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
    style="background:{PAGE_BG};">
    <tr>
      <td align="center" style="padding:32px 16px;">
        <table role="presentation" width="560" cellspacing="0" cellpadding="0"
          style="max-width:560px;width:100%;">
          <tr>
            <td style="padding:0 0 20px;font-family:{FONT_SERIF};
              font-size:22px;font-weight:600;color:{BRAND};">
              Agenda Processual
            </td>
          </tr>
          <tr>
            <td style="background:{SURFACE};border:1px solid #e5e2da;
              border-top:4px solid {accent};padding:28px 28px 32px;">
              <p style="margin:0 0 8px;font-family:{FONT_SANS};font-size:11px;
                font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
                color:{MUTED};">
                {escape(eyebrow)}
              </p>
              <h1 style="margin:0 0 16px;font-family:{FONT_SERIF};font-size:26px;
                line-height:1.25;font-weight:600;color:{BRAND_INK};">
                {escape(heading)}
              </h1>
              {body_html}
              <div style="margin:24px 0 8px;">{_cta(cta_label, cta_url)}</div>
              <p style="margin:16px 0 0;font-family:{FONT_SANS};font-size:13px;
                line-height:1.5;color:{MUTED};">
                {escape(note)}
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding:18px 4px 0;font-family:{FONT_SANS};font-size:12px;
              line-height:1.5;color:{MUTED};">
              {escape(footer)}
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _p(text_html: str) -> str:
    return (
        f'<p style="margin:0 0 12px;font-family:{FONT_SANS};'
        f'font-size:16px;line-height:1.55;color:{BRAND_INK};">{text_html}</p>'
    )


def montar_email_convite(
    *,
    settings: Settings,
    nome: str,
    token: str,
    convidado_por: str,
) -> tuple[str, str, str]:
    link = f"{settings.app_public_url.rstrip('/')}/convite/{token}"
    horas = settings.invite_expire_hours
    subject = "Convite para a Agenda Processual"
    text_body = (
        f"Olá, {nome}.\n\n"
        f"{convidado_por} convidou você para acessar a Agenda Processual.\n\n"
        f"Defina sua senha neste link (válido por {horas}h):\n{link}\n\n"
        "Se você não esperava este convite, ignore este e-mail.\n"
    )
    last_p = (
        f'<p style="margin:0;font-family:{FONT_SANS};font-size:16px;'
        f'line-height:1.55;color:{BRAND_INK};">'
        f"<strong>{escape(convidado_por)}</strong> convidou você para acessar "
        "a Agenda Processual e acompanhar a pauta de prazos.</p>"
    )
    html_body = render_layout(
        preheader="Defina sua senha para acessar a pauta e os vencimentos.",
        eyebrow="Convite",
        heading="Você foi convidado",
        body_html=_p(f"Olá, <strong>{escape(nome)}</strong>.") + last_p,
        cta_label="Definir senha e ativar acesso",
        cta_url=link,
        note=f"O link é válido por {horas} horas.",
        footer="Se você não esperava este convite, ignore este e-mail.",
    )
    return subject, text_body, html_body


def montar_email_alerta(
    *,
    settings: Settings,
    prazo_id: str,
    dias: int,
    vencimento: str,
) -> tuple[str, str, str]:
    link = f"{settings.app_public_url.rstrip('/')}/prazos/{prazo_id}"
    label_dias = "1 dia" if dias == 1 else f"{dias} dias"
    heading = "Prazo amanhã" if dias == 1 else f"Prazo em {label_dias}"
    subject = f"[Agenda Processual] Prazo em {label_dias}"
    text_body = (
        f"Olá,\n\n"
        f"Há um prazo vencendo em {label_dias} ({vencimento}).\n\n"
        f"Os detalhes estão no sistema, após o login. "
        f"Este aviso não inclui dados do processo.\n\n"
        f"Abrir no sistema: {link}\n"
    )
    last_p = (
        f'<p style="margin:0;font-family:{FONT_SANS};font-size:16px;'
        f'line-height:1.55;color:{BRAND_INK};">'
        "Os detalhes estão no sistema, após o login. "
        "Este aviso não inclui dados do processo.</p>"
    )
    html_body = render_layout(
        preheader=(
            f"Prazo vencendo em {label_dias}. Abra o sistema para ver os detalhes."
        ),
        eyebrow="Alerta de prazo",
        heading=heading,
        body_html=_p(
            f"Há um prazo vencendo em <strong>{escape(label_dias)}</strong> "
            f"({escape(vencimento)})."
        )
        + last_p,
        cta_label="Abrir prazo no sistema",
        cta_url=link,
        note="Você recebe porque está como responsável e optou por alertas por e-mail.",
        footer=(
            "Agenda Processual · aviso automático, sem dados do cliente ou do processo."
        ),
        accent=ACCENT_URGENTE if dias <= 1 else BRAND,
    )
    return subject, text_body, html_body
