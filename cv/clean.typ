#let cv = json(sys.inputs.at("cv-data", default: "../data/cv.json"))
#let lang = sys.inputs.at("lang", default: "pt")
#let role = sys.inputs.at("role", default: "data-engineer")
#let L(pt, en, es) = if lang == "en" { en } else if lang == "es" { es } else { pt }
#let month(d) = {
  let n = int(d.slice(5, 7))
  let pt = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
  let en = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
  let es = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
  if lang == "en" { en.at(n - 1) } else if lang == "es" { es.at(n - 1) } else { pt.at(n - 1) }
}
#let date(d) = if d == none { L("Atual", "Present", "Actualidad") } else { month(d) + (if lang == "en" { " " } else { " de " }) + d.slice(0, 4) }
#let period(p) = date(p.start) + " – " + date(p.end)
#let localized(x) = if type(x) == dictionary { x.at(lang, default: x.at("pt", default: "")) } else { x }
#let cert-provider(item) = {
  let value = item.at("providerByLanguage", default: (:)).at(lang, default: item.at("provider", default: none))
  if value == none or ("Não informado", "Not specified", "No especificado").contains(value) { none } else { value }
}
#let has-role(x) = x.roles.contains(role)
#let filtered(xs) = xs.filter(x => has-role(x))
#let green = rgb("238459")
#let slate = rgb("43505B")
#let muted = rgb("64717B")
#let heading = rgb("26323A")
#let section(title) = [#v(8pt)#text(title, size: 11.5pt, weight: "bold", fill: green)#v(2pt)#line(length: 100%, stroke: (paint: rgb("DDE4E0"), thickness: 0.5pt))#v(4pt)]
#let bullet(body) = list(marker: [•], indent: 12pt, body-indent: 7pt, spacing: 2pt, body)

#set page("us-letter", margin: (left: 45pt, right: 45pt, top: 38pt, bottom: 38pt))
#set text(font: "Inter", size: 10pt, fill: slate, lang: if lang == "pt" { "pt" } else { lang })
#set par(leading: 0.4em, justify: false, spacing: 3pt)
#show link: set text(fill: green)

#text(cv.personal.name, size: 20pt, weight: "bold", fill: heading)
#linebreak()
#text(localized(cv.personal.titles.at(role)), size: 11pt, fill: muted)
#linebreak()
#link("mailto:" + cv.personal.email)[#cv.personal.email] #text(" • ", fill: muted)
#text(cv.personal.phone) #text(" • ", fill: muted)
#text(localized(cv.personal.location)) #text(" • ", fill: muted)
#link("https://" + cv.personal.linkedin)[#cv.personal.linkedin] #text(" • ", fill: muted)
#link("https://" + cv.personal.github)[#cv.personal.github]

#section(L("SUMÁRIO", "SUMMARY", "RESUMEN"))
#localized(cv.summary.at(role))

#section(L("EXPERIÊNCIA", "EXPERIENCE", "EXPERIENCIA"))
#for item in filtered(cv.experience) [
  #text(localized(item.role), weight: "bold", fill: heading)#text(" | " + item.company, weight: "semibold")#h(1fr)#text(period(item.period), size: 10pt, fill: muted)
  #linebreak()
  #text(localized(item.location), size: 10pt, fill: muted)
  #v(2pt)
  #for b in filtered(item.bullets) [#bullet(localized(b))#v(1pt)]
  #v(3pt)
]

#section(L("PROJETOS", "PROJECTS", "PROYECTOS"))
#for item in filtered(cv.projects) [
  #block(breakable: false)[
    #text(localized(item.at("nameByLanguage", default: item.name)), weight: "semibold", fill: heading)
    #if item.at("repo", default: none) != none [#h(4pt)#link("https://" + item.repo)[#text(item.repo, size: 9pt)]]
    #v(1pt)
    #let metadata = (
      item.at("institution", default: none),
      if item.at("period", default: none) != none { localized(item.period) } else { none },
      if item.at("participation", default: none) != none { localized(item.participation) } else { none },
      item.at("coordinator", default: none),
    ).filter(value => value != none)
    #if metadata.len() > 0 [#text(metadata.join(" · "), size: 9pt, fill: muted)]
    #v(2pt)
    #text(localized(item.description))
    #if item.at("supervision", default: none) != none [#linebreak()#text(localized(item.supervision), size: 9pt, fill: muted)]
    #if item.at("technologies", default: ()).len() > 0 [#linebreak()#text(item.technologies.join(" · "), size: 9pt, fill: muted)]
    #v(3pt)
  ]
]

#section(L("COMPETÊNCIAS TÉCNICAS", "TECHNICAL SKILLS", "COMPETENCIAS TÉCNICAS"))
#for (key, group) in cv.skills.pairs() [
  #if has-role(group) [#bullet[#text(localized(group.label) + ":", weight: "bold", fill: heading)#h(3pt)#group.items.map(item => group.at("itemTranslations", default: (:)).at(item, default: (:)).at(lang, default: item)).join(", ")]]
]

#section(L("FORMAÇÃO", "EDUCATION", "FORMACIÓN"))
#for item in filtered(cv.education) [
  #grid(
    columns: (1fr, auto),
    column-gutter: 8pt,
    align: (left + top, right + top),
    [#text(localized(item.degree), weight: "semibold", fill: heading)#text(" | " + item.institution + ", " + localized(item.location), size: 10pt)],
    box[#text(period(item.period), size: 10pt, fill: muted)],
  )
  #v(2pt)
]

#section(L("CERTIFICAÇÕES", "CERTIFICATIONS", "CERTIFICACIONES"))
#for item in filtered(cv.certifications) [
  #bullet[#text(localized(item.name), weight: "semibold")#if cert-provider(item) != none [#text(" · " + cert-provider(item), fill: muted)]#if item.at("date", default: none) != none [#text(" · " + date(item.date), fill: muted)]#if item.at("details", default: none) != none [#linebreak()#text("— " + item.at("detailsByLanguage", default: (:)).at(lang, default: item.details), size: 10pt)]]
  #v(1pt)
]

#section(L("IDIOMAS", "LANGUAGES", "IDIOMAS"))
#for item in cv.languages [
  #text(localized(item.language), weight: "semibold")#text(": " + localized(item.level))#if item.at("detail", default: none) != none [#text(" — " + localized(item.detail))]#linebreak()
]
