#import "vendor/imprecv/cv.typ": setrules, showrules, cvheading

#let data = json(sys.inputs.at("path", default: "../data/cv.json"))
#let lang = sys.inputs.at("lang", default: "pt")
#let role = sys.inputs.at("role", default: "data-engineer")
#let localized(value) = if type(value) == dictionary { value.at(lang, default: value.at("pt", default: "")) } else { value }
#let has-role(item) = item.roles.contains(role)
#let selected(items) = items.filter(item => has-role(item))
#let month-name(number) = {
  let pt = ("janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro")
  let en = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
  let es = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre")
  if lang == "en" { en.at(number - 1) } else if lang == "es" { es.at(number - 1) } else { pt.at(number - 1) }
}
#let date(value) = if value == none { if lang == "en" { "Present" } else if lang == "es" { "Actualidad" } else { "Atual" } } else {
  let month = month-name(int(value.slice(5, 7)))
  if lang == "en" { month + " " + value.slice(0, 4) } else { month + " de " + value.slice(0, 4) }
}
#let date-range(period) = date(period.start) + " – " + date(period.end)
#let section-labels = (
  summary: (pt: "SUMÁRIO", en: "SUMMARY", es: "RESUMEN"),
  education: (pt: "FORMAÇÃO", en: "EDUCATION", es: "FORMACIÓN"),
  experience: (pt: "EXPERIÊNCIA", en: "EXPERIENCE", es: "EXPERIENCIA"),
  projects: (pt: "PROJETOS", en: "PROJECTS", es: "PROYECTOS"),
  skills: (pt: "COMPETÊNCIAS TÉCNICAS", en: "TECHNICAL SKILLS", es: "COMPETENCIAS TÉCNICAS"),
  certifications: (pt: "CERTIFICAÇÕES", en: "CERTIFICATIONS", es: "CERTIFICACIONES"),
  languages: (pt: "IDIOMAS", en: "LANGUAGES", es: "IDIOMAS"),
)
#let section(name) = section-labels.at(name).at(lang)
#let uservars = (
  headingfont: "Libertinus Serif",
  bodyfont: "Libertinus Serif",
  fontsize: 10pt,
  linespacing: 6pt,
  sectionspacing: 0pt,
  showAddress: true,
  showNumber: true,
  showTitle: true,
  headingsmallcaps: false,
)
#let personal = (
  personal: (
    name: data.personal.name,
    email: data.personal.email,
    phone: data.personal.phone,
    url: none,
    titles: (localized(data.personal.titles.at(role)),),
    location: (city: localized(data.personal.location)),
    profiles: (
      (url: "https://" + data.personal.linkedin),
      (url: "https://" + data.personal.github),
    ),
  ),
)
#let initialize(doc) = {
  doc = setrules(uservars, doc)
  doc = showrules(uservars, doc)
  set page(paper: "us-letter", margin: 1.25cm)
  doc
}
#show: doc => initialize(doc)

#cvheading(personal, uservars)

== #section("summary")
#localized(data.summary.at(role))

== #section("education")
#let education-items = selected(data.education)
#let institutions = education-items.map(item => item.institution).dedup()
#for institution in institutions [
  #let items = education-items.filter(item => item.institution == institution)
  #block(width: 100%, above: 0.6em, breakable: false)[
    *#institution* #h(1fr) *#localized(items.at(0).location)* \
    #for item in items [
      #text(localized(item.degree), style: "italic") #h(1fr) #date-range(item.period) \
      #v(1pt)
    ]
  ]
]

== #section("experience")
#for item in selected(data.experience) [
  #block(width: 100%, above: 0.8em, breakable: false)[
    *#item.company* #h(1fr) *#localized(item.location)* \
    #text(localized(item.role), style: "italic") #h(1fr) #date-range(item.period) \
    #for bullet in item.bullets.filter(bullet => has-role(bullet)) [
      - #localized(bullet)
    ]
  ]
  #v(0.45em)
]

== #section("projects")
#for item in selected(data.projects) [
  #block(width: 100%, above: 0.6em, breakable: false)[
    #if item.at("repo", default: none) != none [
      *#link("https://" + item.repo)[#localized(item.at("nameByLanguage", default: item.name))]* #h(1fr) #link("https://" + item.repo)[#item.repo]
    ] else [
      *#localized(item.at("nameByLanguage", default: item.name))*
    ]
    #linebreak()
    #let metadata = (
      item.at("institution", default: none),
      if item.at("period", default: none) != none { localized(item.period) } else { none },
      if item.at("participation", default: none) != none { localized(item.participation) } else { none },
      item.at("coordinator", default: none),
    ).filter(value => value != none)
    #if metadata.len() > 0 [
      #text(metadata.join(" · "), style: "italic")
      #linebreak()
    ]
    #localized(item.description)
    #if item.at("supervision", default: none) != none [#linebreak() #localized(item.supervision)]
    #if item.at("technologies", default: ()).len() > 0 [#linebreak() #item.technologies.join(" · ")]
  ]
]

== #section("skills")
#for (_, group) in data.skills.pairs() [
  #if has-role(group) [- *#localized(group.label):* #group.items.map(item => group.at("itemTranslations", default: (:)).at(item, default: (:)).at(lang, default: item)).join(", ")]
]

== #section("certifications")
#for item in data.certifications [
  #let provider = item.at("providerByLanguage", default: (:)).at(lang, default: item.at("provider", default: none))
  #let provider = if (provider == none or ("Não informado", "Not specified", "No especificado").contains(provider)) { none } else { provider }
  #block(width: 100%, above: 0.65em, breakable: false)[
    #grid(
      columns: (1fr, auto),
      column-gutter: 8pt,
      align: (left + top, right + top),
      [*#localized(item.name)*#if provider != none [#text(" · " + provider)]],
      [#if item.at("date", default: none) != none [#date(item.date)]],
    )
  ]
]

== #section("languages")
#for item in data.languages [
  *#localized(item.language):* #localized(item.level)#if item.at("detail", default: none) != none [ — #localized(item.detail)] \
]
