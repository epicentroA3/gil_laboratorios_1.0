Centro Minero SENA - Sistema GIL

print("="*60)
print("ACTUALIZACIÓNDETABLACAPACITACIONES")
print("="*60)

#Verificarsilatabaxse
erificr= "SHOW TABLES LIKE 'cacitaciones'"
esultdo= db_mager.ejecuar_qury(verfcar)

if rsulad:print("\n⚠️Latablacapacitacionesyaexiste")
n("Opcne:")
   i("1. Elmny rrr(SEPERDERÁN LOS DATOS)")
    pri("2. Canclar")
    
    opcio = pu("\nSlccne opción (1/2): ").trip()
ifopcion=="1":
      pin("\n🗑️  Elminandtblexst...")
      ty:
           b_managr.ejecutar_coan("DROPTABLE IF EXISTS cpaciacne")print("✅Tablaelmna")
 xept Exceptin e:
       int(f"❌ Err eliinno tabl: {e}"sys.exit(1)else:
pri("❌ Opcancaa") sys.exit(0)

#Creartablaconestructuracorrecta(igua a scha.sql)
print("\n🔧 Crado tabla capaciones coestructua aualzada...")

sql_ret="""
CRETETABLEIFNOTEXISTScpciacines (
    d INT PRIMARY KEY AUTO_INCREMENT    tituloVARCHAR(300)NOTNULL,
descripcionTEXT,
tipo_capacitacionENUM(talle', 'teial_didcc','gstio_ambi') NOTNULL
   pct VARCHAR(500),
   edicn VARCHAR(200) cantidad_metaINTDEFAULT0,
cantidad_actualINTDEFAULT0
  a VARCHAR(500),
 centaje_vnce DECIMAL(5,2) DEFAULT 0.00,
   uo_horas INT NOT NULL,
   fcha_iicio DATE NOT NULL,
   fha_fi DATE NOT NULL,
    estad ENUM('prramad'en_curso'completadacancelada) DEFAULTid_instructorINT,
fecha_creacionTIMESTAMPDEFAULTCURRENT_TIMESTAMP,    fecha_actualizacion TIMESTAMPDEFAULTCURRENT_TIMESTAMPONUPDATECURRENT_TIMESTAMP,
FOREIGNKEY(id_instructor)REFERENCESusuioid,INDEXidx_tipo(tipo_capacitacion),
INDEXidx_estadoestdo),
    INDEX idx_fchas(fha_iio, fcha_fi)
) ENGINE=InnDBDEAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uniode_c
"""

try:
   db_mnage.ejecutr_mndo(ql_crte)print("✅baadaextosae")
exept Exceptoas :
   pit(f"❌ Errr radtba:{}")
  y.xit(1)
#Insertardatosdeejemplo(igualada.sq)
pint("\n📝Instado dtos de ejempo...")

sql_insert= """
INSERT INTO ci(itucripci,tipo_cionproductomedicionan_mt, cantdd_acu,activiad,porcenaj_avane, duracio_hr,fcha_inici,fch_fiestadoid_instuctVALUESMóduo FomativoIlignciartialAplicadadehermetas IApar geióaboratoromoduo_fomativoInstructorsIAitruore1512Tóri-prácticsbrIA84048048-cplet, 3áens co MobileNetTallersobrmplentciónSistema d ecoimenimplmtadEquiregsro5028Enrnmeno mloMbilNt561490495cplet, 4('D:il didácoGuísigalespbcasgí17Dseñoydcóndguía70449411en_urs, 3Gónl Cambio:Adopó de SstemGL'Programadegestióndelcambiopaa adopcónlnuv istema','gston_mb','Pernlapactad', 'Porcetje e opción', 100, 85, 'Sesionsnsibiización ycapacción85.00,32,'2024-08-15','2024-11-15','en_curso',5),
(Módulo Forativo: Mnnimento PrevCpaciación n técncse mantenmiento preivo nML', 'odo_formavo', 'Técnicos crtficdosténi86Curso hneleaningapcdo7441411en_urs, 4Talle: ComndoVz nLUCIATlrbr uefetioantevzlerUsusenrndosuri330SesonpascnLUCIA084924925mpla',3,MrlDiáctico:ViesutrlesProducvido tuoilsmaeraldidctcVopubidsNúmrovds15,Grabaóydcitutriales644-145en_urs, 5GestiónlCai: Cultuad InvaiónPrgapfenta culuannvaciónavtosrlzadsNúmrovets64Charlsytal movcoals66672494en_urs, 3"""t:db_mnger.ejeur_omando(sql_srt)prin("✅ Dase ejmlo serads")
exet Exepas:print(f"⚠️Errorinsertdo tos: {}")

#Verifir esrurfnl
i("\📋Estrtuald labl:")desc="DCRIBE"estructura=_manager(desormoestructura: - m['Fild']:{campo['ye']}Cngitroscotltado_managercottotal=resultado[0]['total']ifresultadoelse0
#Mostrarresumenportio
podeó:r=b_manager.ejeuar_(ti_apactaCONT*tol avneSMaidd_mtta_aiacin"esmen -ti_aaca']}/{w['ta)✅Tlizada xtoste")f�Tregsr:{to}"+"="*6ACTUALIZACIÓNCOMLETADAprn"=" * 60