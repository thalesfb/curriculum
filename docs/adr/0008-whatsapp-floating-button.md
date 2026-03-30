# ADR-0008: Botão Flutuante de WhatsApp

## Status

Accepted

## Data

2026-03-28

## Contexto

O portfolio precisa de um canal de contato direto e imediato além do formulário de email. WhatsApp é o canal de comunicação mais usado no Brasil e comum em contatos profissionais.

## Decisão

Adicionar um **botão flutuante (FAB)** no canto inferior direito de todas as páginas que redireciona para uma conversa WhatsApp com mensagem pré-determinada.

### Especificações

| Propriedade | Desktop | Tablet | Mobile |
|-------------|---------|--------|--------|
| Tamanho | 56×56px | 52×52px | 48×48px |
| Margem (right/bottom) | 40px | 32px | 20px |
| Border radius | Full (circular) | Full | Full |
| Cor | WhatsApp Green `#25D366` | Igual | Igual |
| Sombra | `0 4px 12px rgba(0,0,0,0.25)` | Igual | Igual |
| Posição | Fixed, bottom-right | Fixed | Fixed |
| Z-index | Acima do conteúdo, abaixo do header | Igual | Igual |

### Link de redirecionamento

```
https://wa.me/5549998048695?text=Olá%20Thales!%20Vi%20seu%20portfólio%20e%20gostaria%20de%20conversar%20sobre%20um%20projeto.
```

### Mensagem pré-determinada por idioma

| Idioma | Mensagem |
|--------|----------|
| PT | "Olá Thales! Vi seu portfólio e gostaria de conversar sobre um projeto." |
| EN | "Hi Thales! I saw your portfolio and would like to discuss a project." |
| ES | "¡Hola Thales! Vi tu portafolio y me gustaría conversar sobre un proyecto." |

### Implementação (HTML/CSS)

```html
<a href="https://wa.me/5549998048695?text=..."
   class="whatsapp-fab"
   target="_blank"
   rel="noopener noreferrer"
   aria-label="Conversar no WhatsApp">
  <svg><!-- WhatsApp icon --></svg>
</a>
```

```css
.whatsapp-fab {
  position: fixed;
  bottom: 40px;
  right: 40px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #25D366;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
  z-index: 50;
  transition: transform 0.2s ease;
}
.whatsapp-fab:hover { transform: scale(1.1); }
```

## Racional

1. **WhatsApp é ubíquo no Brasil** — principal canal de contato profissional
2. **Mensagem pré-determinada** reduz fricção — o visitante não precisa pensar no que escrever
3. **Botão flutuante** é padrão reconhecido (99% dos sites comerciais brasileiros)
4. **Sem dependência de serviço** — usa `wa.me` API oficial do WhatsApp

## Consequências

### Positivas

- Canal de contato imediato e direto
- Maior taxa de conversão que formulário de email
- Zero dependências (link direto para wa.me)
- Mensagem pré-formatada com contexto

### Negativas

- Ocupa espaço visual permanente na tela
- Pode cobrir conteúdo no mobile (mitigação: margem adequada)

## Figma

- Componente: `WhatsApp Button` na página Components
- Instâncias flutuantes (absolute) em Desktop, Tablet, Mobile
