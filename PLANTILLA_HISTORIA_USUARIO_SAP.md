# Plantilla — Historia de Usuario SAP

Plantilla reutilizable para documentar historias de usuario en proyectos de implementación, evolutivos o soporte SAP. Copia el bloque completo por cada historia nueva.

---

## 1. Encabezado

| Campo | Valor |
|---|---|
| **ID** | US-AAAA-### |
| **Título** | *(frase corta y accionable, ej. "Bloquear contabilización de facturas sin OC asociada")* |
| **Módulo SAP** | *(FI, CO, MM, SD, PP, QM, HCM, Fiori/UI5, BASIS, ...)* |
| **Tipo** | *(Customizing / Desarrollo ABAP / Fiori App / Interfaz / Reporte / Autorización)* |
| **Prioridad** | *(Alta / Media / Baja)* |
| **Sprint / Release** | |

## 2. Narrativa

> Como **[rol/perfil de usuario]**
> Quiero **[funcionalidad o comportamiento deseado]**
> Para **[beneficio de negocio / objetivo]**

*El rol debe ser específico al negocio (ej. "analista de cuentas por pagar", no solo "usuario").*

## 3. Contexto funcional

- **Proceso de negocio afectado**: *(ej. Order-to-Cash, Procure-to-Pay)*
- **Transacciones SAP involucradas**: *(t-codes actuales o nuevas)*
- **Datos maestros relevantes**: *(materiales, clientes, proveedores, centros de costo)*
- **Organización donde aplica**: *(sociedad, centro, división, org. de ventas)*

## 4. Criterios de aceptación

- Dado que *[condición inicial en SAP]*
- Cuando *[acción del usuario/transacción]*
- Entonces *[resultado esperado, incluyendo mensajes de error/validación]*

*(Repetir el bloque Given/When/Then por cada escenario)*

## 5. Reglas de negocio

- *[lógica específica que debe cumplirse: validaciones, cálculos, condiciones de bloqueo, jerarquías de aprobación]*

## 6. Impacto técnico

- **Objetos SAP afectados**: tablas, estructuras, BAdIs, exits, enhancement points
- **Interfaces**: IDocs, RFCs, BAPIs, API/OData (si aplica integración)
- **Impacto en otros módulos**: *(ej. un cambio en MM que afecta FI)*

## 7. No funcionales / restricciones

- **Autorizaciones y roles (PFCG)** requeridos
- **Performance**: *(si involucra procesos batch o grandes volúmenes)*
- **Ambientes de prueba**: DEV → QA → PRD, y necesidad de datos de prueba específicos

## 8. Dependencias

- *[otras historias, transportes o desarrollos previos necesarios]*

## 9. Definition of Done

- [ ] Desarrollado y unit-testeado
- [ ] Transportado a QA
- [ ] Caso de prueba ejecutado y validado por el usuario clave (key user)
- [ ] Documentación funcional/técnica actualizada
- [ ] Aprobado por el dueño de proceso

## 10. Adjuntos

- *[mockups (Fiori), diagramas de proceso, ejemplos de datos, capturas de mensajes de error actuales]*
