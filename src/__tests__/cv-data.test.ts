import { describe, it, expect } from 'vitest';
import cvData from '../../data/cv.json';
import { ui } from '../i18n/ui';

const LANGUAGES = ['pt', 'en', 'es'];
const ROLES = ['data-engineer', 'backend', 'devops', 'management', 'frontend'];

describe('cv.json schema validation', () => {
  it('has meta section with required fields', () => {
    expect(cvData.meta).toBeDefined();
    expect(cvData.meta.version).toMatch(/^\d+\.\d+\.\d+$/);
    expect(cvData.meta.languages).toEqual(LANGUAGES);
    expect(cvData.meta.roles).toEqual(ROLES);
  });

  it('has personal section with required fields', () => {
    expect(cvData.personal.name).toBeTruthy();
    expect(cvData.personal.email).toMatch(/@/);
    expect(cvData.personal.phone).toBeTruthy();
    expect(cvData.personal.linkedin).toBeTruthy();
    expect(cvData.personal.github).toBeTruthy();
  });

  it('personal.location has all languages', () => {
    for (const lang of LANGUAGES) {
      expect((cvData.personal.location as Record<string, string>)[lang]).toBeTruthy();
    }
  });

  it('includes the approved Lattes profile URL', () => {
    expect(cvData.personal.lattes).toBe('http://lattes.cnpq.br/9042504768658064');
  });

  it('uses the approved contact email', () => {
    expect(cvData.personal.email).toBe('thalesfb15@gmail.com');
  });

  it('personal.titles covers all roles and languages', () => {
    for (const role of ROLES) {
      const titles = cvData.personal.titles as Record<string, Record<string, string>>;
      expect(titles[role]).toBeDefined();
      for (const lang of LANGUAGES) {
        expect(titles[role][lang], `Missing title for ${role}/${lang}`).toBeTruthy();
      }
    }
  });

  it('summary covers all roles and languages', () => {
    for (const role of ROLES) {
      const summary = cvData.summary as Record<string, Record<string, string>>;
      expect(summary[role]).toBeDefined();
      for (const lang of LANGUAGES) {
        expect(summary[role][lang], `Missing summary for ${role}/${lang}`).toBeTruthy();
      }
    }
  });

  it('matches the approved PDF summary for the data-engineer role', () => {
    expect(cvData.summary['data-engineer']).toEqual({
      pt: 'Profissional com ampla experiência em análise de dados, engenharia de software e automação industrial. Especializado no uso de Python, Power BI, SQL, Django, NGINX e práticas DevOps, com foco na otimização de processos, eficiência operacional e entrega de soluções estratégicas. Proativo, com sólida capacidade de liderança e trabalho em equipe, busca contribuir para projetos inovadores e desafiadores.',
      en: 'Professional with extensive experience in data analysis, software engineering, and industrial automation. Specialized in Python, Power BI, SQL, Django, NGINX, and DevOps practices, with a focus on process optimization, operational efficiency, and delivering strategic solutions. Proactive with solid leadership capabilities and teamwork skills, seeking to contribute to innovative and challenging projects.',
      es: 'Full Stack Data Engineer y Founder con historial de entrega de soluciones tecnológicas end-to-end. Especialista en combinar ingeniería de software (Python, Django, NGINX), automatización DevOps e inteligencia de datos para resolver cuellos de botella de negocios. Redujo costos operacionales industriales en hasta un 70% al diseñar sistemas de control automatizados. Sólida experiencia en la construcción de pipelines de Machine Learning reproducibles, aprovechando la visión de negocios para crear arquitecturas escalables que generan impacto financiero y operacional directo.',
    });
  });

  it('keeps approved Portuguese accents in education and summaries', () => {
    expect(cvData.education.map(entry => entry.degree.pt)).toContain('Bacharelado em Ciência da Computação');
    expect(ui.pt['cv.education']).toContain('FORMAÇÃO');
    expect(cvData.summary['data-engineer'].pt).toContain('Profissional com ampla experiência');
  });

  it('has the approved IFC period', () => {
    const ifc = cvData.education.find(entry => entry.institution === 'Instituto Federal Catarinense');
    expect(ifc?.period).toEqual({ start: '2023-02', end: '2026-12' });
  });

  it('marks AWS Academy Cloud Architecting as in progress', () => {
    const architecting = cvData.certifications.find(certification => certification.name.pt === 'AWS Academy Cloud Architecting');
    expect(architecting?.provider).toBe('AWS Academy');
    expect(architecting?.status).toBe('in-progress');
  });

  it('keeps both Latinoware events and the confirmed 2025 provider', () => {
    const latinoware2025 = cvData.certifications.find(certification => certification.name.pt === 'Latinoware 2025 (28h)');
    const latinoware2014 = cvData.certifications.find(certification => certification.name.pt === 'Latinoware 2014');
    expect(latinoware2025?.provider).toBe('Itaipu Parquetec');
    expect(latinoware2014).toBeDefined();
    expect(latinoware2014).not.toHaveProperty('provider');
    expect(latinoware2014).not.toHaveProperty('hours');
  });

  it('includes both approved SENAI courses', () => {
    const senai = cvData.education.filter(entry => entry.institution === 'SENAI');
    expect(senai.map(entry => entry.degree.pt)).toEqual([
      'Aprendizagem Industrial de Suporte e Manutenção em Microcomputadores e Redes Locais',
      'Operador de Computador',
    ]);
  });

  it('preserves confirmed skills and language proficiency', () => {
    expect(cvData.skills['languages-backend'].items).toEqual(expect.arrayContaining(['Java', 'Spring Boot']));
    expect(cvData.skills['ml-data'].items).toEqual(expect.arrayContaining(['Scikit-learn', 'XGBoost', 'TensorFlow']));
    expect(cvData.skills.frontend.items).toEqual(expect.arrayContaining(['React', 'TypeScript']));
    expect(cvData.languages.map(entry => [entry.language.pt, entry.level.pt])).toEqual([
      ['Português', 'Nativo'],
      ['Inglês', 'Intermediário'],
      ['Espanhol', 'Intermediário'],
    ]);
  });

  it('includes every dated Alura course and matches group hours and periods', () => {
    type CourseExpectation = [string, number, string | null, string | null];
    const expectedGroups: Array<{ name: string; hours: number; courses: CourseExpectation[]; date?: string }> = [
      {
        name: 'Trilha Django REST Framework', hours: 30, courses: [
          ['Django REST Framework: construindo APIs RESTful do Zero', 8, '2024-07', '2024-08'],
          ['Django REST Framework: trabalhando com validações, paginação, filtros e versionamento em uma API', 6, '2024-07', '2025-05'],
          ['Django REST Framework: trabalhando com permissões, documentação, limitações, CORS e deploy na AWS', 8, '2025-05', '2025-05'],
          ['Django REST Framework: trabalhando com testes unitários e de integração', 8, '2025-05', '2025-09'],
        ],
      },
      {
        name: 'Back-end', hours: 127, courses: [
          ['Python: começando com a linguagem', 12, '2023-05', '2023-06'],
          ['Python: avançando na linguagem', 12, '2023-06', '2023-07'],
          ['Python: avançando na orientação a objetos', 10, '2023-07', '2023-08'],
          ['Python Collections parte 1: listas e tuplas', 8, '2023-08', '2023-08'],
          ['Python Collections parte 2: conjuntos e dicionários', 9, '2023-08', '2023-08'],
          ['API com Django 3: Django Rest Framework', 8, '2024-03', '2024-04'],
          ['API com Django 3: Validações, buscas, filtros e deploy', 8, '2024-04', '2024-06'],
          ['API com Django 3: Versionamento, cabeçalhos e CORS', 6, '2024-06', '2024-06'],
          ['String em Python: extraindo informações de uma URL', 8, '2023-08', '2023-08'],
          ['Python e TDD: explorando testes unitários', 8, '2023-11', '2024-04'],
          ['Django: templates e boas práticas', 8, '2024-02', '2024-02'],
          ['Django: persistência de dados e Admin', 10, '2024-02', '2024-05'],
          ['Python: entendendo a Orientação a Objetos', 12, '2023-06', '2023-07'],
          ['Git e GitHub: dominando controle de versão de código', 8, '2025-09', '2025-09'],
        ],
      },
      { name: 'Dados', hours: 198, courses: [
        ['Business Intelligence: trabalhando com Data Warehouse', 12, '2022-10', '2023-05'],
        ['Excel: simulação e análise de cenários', 6, '2022-09', '2022-09'],
        ['Análise de dados: cálculos, padrões e estratégias com Excel', 6, '2022-09', '2022-09'],
        ['Excel procv: lógica booleana e busca por valores', 12, '2022-09', '2022-09'],
        ['Excel: tabelas dinâmicas e dashboards', 10, '2022-09', '2022-09'],
        ['Excel: criação de macros e automatização de tarefas', 12, '2022-09', '2022-09'],
        ['Excel: personalizando e automatizando tarefas com VBA', 8, '2022-08', '2022-08'],
        ['Power BI Desktop: tratamento de dados no Power Query', 8, '2022-10', '2023-01'],
        ['Excel VBA: automatize tarefas diárias mesmo não sendo programador', 8, '2022-09', '2022-09'],
        ['Excel VBA: criando Formulários para facilitar a entrada de dados nas planilhas', 8, '2022-08', '2022-09'],
        ['Excel VBA 3: criando conexão com o Outlook Application', 10, '2022-09', '2022-09'],
        ['Excel VBA 4: criando conexão com Access', 10, '2022-09', '2022-09'],
        ['Power BI Desktop: construindo meu primeiro dashboard', 8, '2022-09', '2022-10'],
        ['Dashboard com Power BI: visualizando dados', 8, '2022-10', '2022-12'],
        ['Modelagem de banco de dados: entidades, relacionamentos e atributos', 8, '2023-04', '2023-07'],
        ['Modelagem de banco de dados relacional: modelagem lógica e física', 8, '2023-07', '2023-08'],
        ['Modelagem de banco de dados relacional: normalização', 6, '2023-08', '2023-08'],
        ['Python para Dados: primeiros passos', 10, '2023-07', '2023-09'],
        ['Python para Dados: trabalhando com funções, estruturas de dados e exceções', 8, '2023-07', '2023-10'],
        ['Pandas: conhecendo a biblioteca', 8, '2023-07', '2023-11'],
        ['Pandas I/O: trabalhando com diferentes formatos de arquivos', 8, '2023-07', '2024-02'],
        ['Regressão: aprimorando os resultados com XGBoost', 8, '2025-05', '2025-05'],
        ['Machine Learning: classificação com SKLearn', 8, '2025-04', '2025-04'],
      ] },
      { name: 'DevOps', hours: 14, courses: [
        ['NGINX: servidor Web, Proxy Reverso e API Gateway', 6, '2024-07', '2024-07'],
        ['NGINX Parte 2: performance, FastCGI e HTTPS', 8, '2024-07', '2024-07'],
      ] },
      { name: 'Inteligência Artificial', hours: 16, courses: [
        ['GitHub Copilot e ChatGPT: impulsionando seu desenvolvimento com IA', 8, '2023-06', '2023-08'],
        ['Excel com IA: mapeando e evoluindo processos', 8, '2023-08', '2023-09'],
      ] },
      { name: 'UX & Design', hours: 8, courses: [
        ['Figma: Conhecendo o programa', 8, '2025-12', '2025-12'],
      ] },
      { name: 'Front-end', hours: 2, courses: [
        ['Carreira Desenvolvedor(a) Front-end React: boas-vindas e primeiros passos', 2, '2025-10', '2025-11'],
      ] },
      { name: 'Inglês', hours: 4, courses: [
        ['Inglês para devs: Meeting - Creating and embedding contact forms for a client', 4, '2022-09', '2022-10'],
      ] },
      { name: 'Imersão Engenharia de Software: Dev na Era da IA', hours: 4, date: '2026-11', courses: [
        ['Imersão Engenharia de Software: Dev na Era da IA', 4, null, null],
      ] },
    ];
    const expectedNames = expectedGroups.map(group => group.name);
    const alura = cvData.certifications.filter(certification => certification.provider === 'Alura');
    expect(alura.map(group => group.name.pt)).toEqual(expectedNames);
    const certificateUrl = 'https://cursos.alura.com.br/user/thalesfb/fullCertificate/1ec4275c873ec751eabead5b304ef7f8';

    for (const expected of expectedGroups) {
      const group = alura.find(item => item.name.pt === expected.name)!;
      expect(group.credentialUrl).toBe(certificateUrl);
      expect(group.hours).toBe(expected.hours);
      expect(group.courses).toHaveLength(expected.courses.length);
      expect(group.courses.map(course => course.pt)).toEqual(expected.courses.map(([name]) => name));
      expect(group.courses.reduce((sum, course) => sum + course.hours, 0)).toBe(group.hours);
      expect(group.date).toBe(expected.date);

      const expectedCoursePeriods = expected.courses.map(([, , start, end]) => start && end ? { start, end } : undefined);
      expect(group.courses.map(course => course.period)).toEqual(expectedCoursePeriods);
      const datedCourses = expected.courses.filter(([, , start, end]) => start && end);
      if (datedCourses.length) {
        const starts = datedCourses.map(([, , start]) => start!).sort();
        const ends = datedCourses.map(([, , , end]) => end!).sort();
        expect(group.period).toEqual({ start: starts[0], end: ends.at(-1) });
      } else {
        expect(group.period).toBeUndefined();
      }
      for (const course of group.courses) {
        expect(course.en).toBe(course.pt);
        expect(course.es).toBe(course.pt);
      }
    }
  });

  it('keeps the three locale translations for approved CV fields', () => {
    for (const entry of cvData.education) {
      for (const lang of LANGUAGES) expect(entry.degree[lang]).toBeTruthy();
    }
    for (const entry of cvData.certifications) {
      for (const lang of LANGUAGES) expect(entry.name[lang]).toBeTruthy();
    }
    for (const entry of cvData.experience) {
      for (const lang of LANGUAGES) {
        expect(entry.role[lang]).toBeTruthy();
        for (const bullet of entry.bullets) expect(bullet[lang]).toBeTruthy();
      }
    }
  });

  it('keeps literal CMAQ and TBC descriptions and the approved CPEL title', () => {
    const cmaq = cvData.experience.find(entry => entry.company === 'CMAQ');
    const tbc = cvData.experience.find(entry => entry.company === 'TBC NETWORK EIRELI');
    const cpel = cvData.experience.find(entry => entry.company === 'CPEL');
    expect(cmaq?.bullets[0].pt).toBe('Gerenciei estoque e controle de mercadorias, implementando melhorias nos processos de cadastro e atendimento ao cliente.');
    expect(tbc?.bullets[0].pt).toBe('Realizei manutenção de equipamentos de redes e análise de tráfego, garantindo infraestrutura eficiente.');
    expect(cpel?.role.pt).toBe('Full Stack Data Engineer with Software and DevOps Expertise');
  });

  it('omits the Optimizr location and keeps six bullets in all languages', () => {
    const opt = cvData.experience.find(entry => entry.company === 'OPTIMIZR');
    expect(opt).not.toHaveProperty('location');
    expect(opt?.bullets.map(bullet => bullet.pt)).toEqual([
      'Fundei e lidero a Optimizr, consultoria de automação, dados e software sob medida, do diagnóstico de processos ao MVP em produção.',
      'Mapeio processos (AS-IS/TO-BE) e priorizo automações pelo retorno, com arquitetura adaptada aos sistemas que o cliente já usa.',
      'Desenvolvo aplicações full-stack (Django, TypeScript/React) com CI/CD, integrações via APIs e automações em Python que eliminam tarefas manuais.',
      'Construo pipelines de dados e dashboards em Power BI; para clientes corporativos, zerei o tempo de espera na geração de relatórios.',
      'Entreguei plataformas para varejo, alimentação e comércio: delivery com catálogo de 200+ produtos, gestão unificada de vendas, pedidos, produção e pagamentos, e centralização financeira e operacional.',
      'Opero a infraestrutura dos clientes em Linux, Docker e NGINX (SSL/TLS), com suporte contínuo e treinamento das equipes.',
    ]);
    expect(opt?.bullets.map(bullet => bullet.en)).toEqual([
      'I founded and lead Optimizr, a consulting firm for automation, data, and custom software, from process diagnosis through an MVP in production.',
      'I map processes (AS-IS/TO-BE) and prioritize automations by return, with architecture adapted to the systems the client already uses.',
      'I develop full-stack applications (Django, TypeScript/React) with CI/CD, API integrations, and Python automations that eliminate manual tasks.',
      'I build data pipelines and Power BI dashboards; for corporate clients, I eliminated wait time for report generation.',
      'I delivered platforms for retail, food service, and commerce: delivery with a catalog of 200+ products, unified management of sales, orders, production, and payments, and financial and operational centralization.',
      'I operate clients’ infrastructure on Linux, Docker, and NGINX (SSL/TLS), with ongoing support and team training.',
    ]);
    expect(opt?.bullets.map(bullet => bullet.es)).toEqual([
      'Fundé y lidero Optimizr, una consultoría de automatización, datos y software a medida, desde el diagnóstico de procesos hasta un MVP en producción.',
      'Mapeo procesos (AS-IS/TO-BE) y priorizo automatizaciones según su retorno, con una arquitectura adaptada a los sistemas que el cliente ya utiliza.',
      'Desarrollo aplicaciones full-stack (Django, TypeScript/React) con CI/CD, integraciones mediante API y automatizaciones en Python que eliminan tareas manuales.',
      'Construyo pipelines de datos y dashboards en Power BI; para clientes corporativos, eliminé el tiempo de espera en la generación de informes.',
      'Entregué plataformas para comercio minorista, alimentación y comercio: delivery con un catálogo de más de 200 productos, gestión unificada de ventas, pedidos, producción y pagos, y centralización financiera y operativa.',
      'Opero la infraestructura de los clientes en Linux, Docker y NGINX (SSL/TLS), con soporte continuo y capacitación de los equipos.',
    ]);
    expect(opt?.bullets).toHaveLength(6);
    for (const bullet of opt?.bullets ?? []) {
      expect(bullet.en).toBeTruthy();
      expect(bullet.es).toBeTruthy();
      expect(bullet.roles).toEqual(opt?.roles);
    }
  });

  it('retains the approved CPEL bullets', () => {
    const cpel = cvData.experience.find(entry => entry.company === 'CPEL');
    expect(cpel?.bullets.map(bullet => bullet.pt)).toEqual(expect.arrayContaining([
      'Desenvolvi um sistema de controle de produção que otimizou a eficiência operacional e reduziu desperdícios.',
      'Criei relatórios digitais que integraram métricas de qualidade, aumentando significativamente os padrões de produção.',
      'Implementei processos analíticos para monitoramento de energia gerada pela usina hidrelétrica, apoiando decisões estratégicas.',
      'Desenvolvi dashboards avançados em Power BI para análise de tendências e suporte à alta gestão.',
      'Projetei um software de gestão integrada, otimizando fluxos de trabalho e comunicação entre setores.',
    ]));
  });

  it('removes client counts and the retail client identity from CV content', () => {
    const content = JSON.stringify(cvData).toLowerCase();
    expect(content).not.toContain('baianos');
    expect(content).not.toContain('4 clientes');
    expect(content).not.toContain('4 corporate clients');
    expect(content).not.toContain('baianosconveniencia.com');
  });

  it('every experience entry has required fields', () => {
    for (const exp of cvData.experience) {
      expect(exp.company).toBeTruthy();
      expect(exp.period.start).toMatch(/^\d{4}-\d{2}$/);
      for (const lang of LANGUAGES) {
        expect((exp.role as Record<string, string>)[lang], `Missing role ${lang} for ${exp.company}`).toBeTruthy();
        if (exp.location) {
          expect((exp.location as Record<string, string>)[lang], `Missing location ${lang} for ${exp.company}`).toBeTruthy();
        }
      }
    }
  });

  it('every project has required fields in all languages', () => {
    for (const proj of cvData.projects) {
      expect(proj.name).toBeTruthy();
      if (proj.repo) expect(proj.repo).toBeTruthy();
      expect(Array.isArray(proj.technologies)).toBe(true);
      for (const lang of LANGUAGES) {
        expect((proj.description as Record<string, string>)[lang], `Missing description ${lang} for ${proj.name}`).toBeTruthy();
      }
      if (proj.nameByLanguage) {
        for (const lang of LANGUAGES) expect(proj.nameByLanguage[lang]).toBeTruthy();
      }
    }
  });

  it('lists sourced AI projects not already represented in the CV', () => {
    const aiImplementations = cvData.projects.find(project => project.repo === 'github.com/thalesfb/AI');
    const cursorAgents = cvData.projects.find(project => project.repo === 'github.com/thalesfb/cursor-agents');

    expect(aiImplementations?.nameByLanguage).toEqual({
      pt: 'Implementações de Inteligência Artificial',
      en: 'Artificial Intelligence Implementations',
      es: 'Implementaciones de Inteligencia Artificial',
    });
    expect(aiImplementations?.technologies).toEqual(['BFS', 'UCS', 'DFS']);
    expect(aiImplementations?.roles).toEqual(['data-engineer', 'backend']);
    expect(aiImplementations?.description.pt).toContain('buscas BFS, UCS e DFS');
    expect(aiImplementations?.description.en).toContain('BFS, UCS, and DFS searches');
    expect(aiImplementations?.description.es).toContain('búsquedas BFS, UCS y DFS');

    expect(cursorAgents).toBeUndefined();
    expect(JSON.stringify(cvData)).not.toContain('cursor-agents');
  });

  it('keeps the IFC capstone project title and translations', () => {
    const project = cvData.projects.find(entry => entry.name === 'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais');
    expect(project?.repo).toBe('github.com/thalesfb/ccw');
    expect(project?.nameByLanguage).toEqual({
      pt: 'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais',
      en: 'Personalized Mathematics Teaching: Opportunities and Computational Techniques',
      es: 'Enseñanza Personalizada de Matemáticas: Oportunidades y Técnicas Computacionales',
    });
    expect(project?.supervision).toEqual({
      pt: 'Orientador: Rafael Zanin; coorientador: Manassés Ribeiro.',
      en: 'Advisor: Rafael Zanin; co-advisor: Manassés Ribeiro.',
      es: 'Tutor: Rafael Zanin; cotutor: Manassés Ribeiro.',
    });
  });

  it('includes both Lattes research projects with localized metadata and sourced activities', () => {
    const infrastructure = cvData.projects.find(project => project.name === 'Infraestrutura de comunicação industrial: implantação e integração de redes e protocolos para automação de processos');
    const platform = cvData.projects.find(project => project.name === 'Plataforma de Decisão Compartilhada Humano-Máquina para Processos Industriais');
    expect(infrastructure?.nameByLanguage).toEqual({
      pt: 'Infraestrutura de comunicação industrial: implantação e integração de redes e protocolos para automação de processos',
      en: 'Industrial Communication Infrastructure: Deployment and Integration of Networks and Protocols for Process Automation',
      es: 'Infraestructura de comunicación industrial: implementación e integración de redes y protocolos para la automatización de procesos',
    });
    expect(platform?.nameByLanguage).toEqual({
      pt: 'Plataforma de Decisão Compartilhada Humano-Máquina para Processos Industriais',
      en: 'Human-Machine Shared Decision Platform for Industrial Processes',
      es: 'Plataforma de Decisión Compartida Humano-Máquina para Procesos Industriales',
    });
    for (const project of [infrastructure, platform]) {
      expect(project?.period).toEqual({ pt: '2026–atual', en: '2026–present', es: '2026–actualidad' });
      expect(project?.participation).toEqual({ pt: 'Estudante voluntário', en: 'Volunteer student', es: 'Estudiante voluntario' });
      expect(project?.coordinator).toBe('Frederico de Oliveira Santos');
      expect(project?.institution).toBe('IFC Campus Videira');
      expect(project?.sourceUrl).toBe('http://lattes.cnpq.br/9042504768658064');
      expect(project?.technologies).toEqual([]);
      for (const lang of LANGUAGES) expect(project?.description[lang]).toBeTruthy();
    }
    expect(infrastructure?.roles).toEqual(['devops', 'data-engineer']);
    expect(infrastructure?.description.pt).toContain('cabeamento e equipamentos');
    expect(infrastructure?.description.en).toContain('cabling and equipment');
    expect(infrastructure?.description.es).toContain('cableado y equipos');
    expect(platform?.roles).toEqual(['data-engineer', 'backend']);
    expect(platform?.description.pt).toContain('deliberação multiagente');
    expect(platform?.description.en).toContain('multi-agent deliberation');
    expect(platform?.description.es).toContain('deliberación multiagente');
  });

  it('keeps English text free of unsupported zero-downtime claims', () => {
    expect(JSON.stringify(cvData).toLowerCase()).not.toContain('zero downtime');
  });

  it('keeps approved project descriptions aligned across languages', () => {
    const infrastructure = cvData.projects.find(project => project.name === 'Infrastructure & Web Services');
    const structures = cvData.projects.find(project => project.name === 'Data Structures');
    expect(infrastructure?.description.en.toLowerCase()).not.toContain('zero downtime');
    expect(structures?.description.en).toBe('Implementation of algorithms and fundamental data structures in C.');
    expect(structures?.description.es).toBe('Implementación de algoritmos y estructuras de datos fundamentales en C.');
  });

  it('uses idiomatic and consistently capitalized English and Spanish labels', () => {
    expect(cvData.heroSubtitle.backend.en).toContain('best practices');
    expect(cvData.heroSubtitle.management.es.startsWith('Liderazgo')).toBe(true);
    expect(cvData.skills.leadership.label.es).toBe('Gestión y Liderazgo');
  });

  it('has localized, grouped Alura course lists with official Portuguese names', () => {
    const alura = cvData.certifications.filter(certification => certification.provider === 'Alura');
    for (const group of alura) {
      expect(group.courses?.length).toBeGreaterThan(0);
      for (const course of group.courses ?? []) {
        expect(course.pt).toBeTruthy();
        expect(course.en).toBeTruthy();
        expect(course.es).toBeTruthy();
      }
    }
    expect(JSON.stringify(cvData.certifications)).not.toMatch(/Não informado|Not specified|No especificado/);
  });

  it('describes the IFC TCC as in progress with expected completion in December 2026', () => {
    const tcc = cvData.projects.find(project => project.name === 'Ensino Personalizado de Matemática: Oportunidades e Técnicas Computacionais');
    expect(tcc?.description.pt).toContain('Projeto de TCC (PTC) apresentado no IFC Videira; TCC em desenvolvimento, conclusão prevista em DEZ 2026.');
    expect(tcc?.description.en).toContain('Capstone project (PTC) presented at IFC Videira; TCC in development, expected completion in DEC 2026.');
    expect(tcc?.description.es).toContain('Proyecto de TCC (PTC) presentado en IFC Videira; TCC en desarrollo, conclusión prevista para DIC 2026.');
  });
});
