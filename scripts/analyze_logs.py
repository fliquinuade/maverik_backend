#!/usr/bin/env python3
"""
Script para análisis y monitoreo de logs de Maverik Backend.

Proporciona herramientas para:
- Análizar rendimiento de endpoints
- Monitorear comunicación con RAG
- Detectar errores frecuentes
- Generar reportes de uso

Uso:
    python scripts/analyze_logs.py --report performance
    python scripts/analyze_logs.py --report errors --last-hours 24
    python scripts/analyze_logs.py --report rag-performance
"""

import argparse
import json
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


def load_logs(log_file: str, last_hours: int = None) -> List[Dict]:
    """
    Cargar logs desde archivo JSON.
    """
    logs = []
    log_path = Path(log_file)
    
    if not log_path.exists():
        print(f"❌ Archivo de log no encontrado: {log_file}")
        return logs
    
    # Calcular timestamp límite si se especifica
    cutoff_time = None
    if last_hours:
        cutoff_time = datetime.utcnow() - timedelta(hours=last_hours)
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    
                    # Filtrar por tiempo si se especifica
                    if cutoff_time:
                        log_time = datetime.fromisoformat(log_entry['timestamp'].replace('Z', '+00:00'))
                        if log_time < cutoff_time:
                            continue
                    
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    continue  # Saltar líneas malformadas
                    
    except Exception as e:
        print(f"❌ Error leyendo logs: {e}")
        
    return logs


def analyze_performance(logs: List[Dict]) -> Dict[str, Any]:
    """
    Analizar performance de endpoints.
    """
    endpoint_stats = defaultdict(list)
    
    for log in logs:
        if log.get('logger') == 'maverik.requests' and 'duration_ms' in log:
            endpoint = log.get('endpoint', 'unknown')
            duration = log.get('duration_ms', 0)
            status = log.get('http_status', 0)
            
            endpoint_stats[endpoint].append({
                'duration': duration,
                'status': status,
                'timestamp': log['timestamp']
            })
    
    # Calcular estadísticas por endpoint
    results = {}
    for endpoint, requests in endpoint_stats.items():
        durations = [r['duration'] for r in requests]
        statuses = [r['status'] for r in requests]
        
        if durations:
            results[endpoint] = {
                'total_requests': len(requests),
                'avg_duration_ms': round(sum(durations) / len(durations), 2),
                'min_duration_ms': min(durations),
                'max_duration_ms': max(durations),
                'success_rate': len([s for s in statuses if 200 <= s < 400]) / len(statuses) * 100,
                'error_rate': len([s for s in statuses if s >= 400]) / len(statuses) * 100,
                'status_distribution': dict(Counter(statuses))
            }
    
    return results


def analyze_rag_performance(logs: List[Dict]) -> Dict[str, Any]:
    """
    Analizar performance de comunicación con RAG.
    """
    rag_communications = []
    
    for log in logs:
        if log.get('logger') == 'maverik.rag':
            rag_communications.append(log)
    
    if not rag_communications:
        return {"message": "No se encontraron comunicaciones con RAG"}
    
    # Separar por tipo de evento
    successes = []
    timeouts = []
    errors = []
    
    for log in rag_communications:
        message = log.get('message', '')
        if 'success' in message:
            response_time = log.get('response_time_ms', 0)
            successes.append(response_time)
        elif 'timeout' in message.lower() or 'timed out' in message.lower():
            timeouts.append(log)
        elif log.get('level') == 'ERROR':
            errors.append(log)
    
    results = {
        'total_communications': len(rag_communications),
        'successful_communications': len(successes),
        'timeout_count': len(timeouts),
        'error_count': len(errors)
    }
    
    if successes:
        results.update({
            'avg_response_time_ms': round(sum(successes) / len(successes), 2),
            'min_response_time_ms': min(successes),
            'max_response_time_ms': max(successes),
            'success_rate': len(successes) / len(rag_communications) * 100
        })
    
    return results


def analyze_errors(logs: List[Dict]) -> Dict[str, Any]:
    """
    Analizar errores y excepciones.
    """
    errors = []
    error_types = Counter()
    error_contexts = Counter()
    
    for log in logs:
        if log.get('level') in ['ERROR', 'CRITICAL']:
            errors.append(log)
            
            # Contar tipos de error
            error_type = log.get('error_type', 'unknown')
            error_types[error_type] += 1
            
            # Contar contextos donde ocurren errores
            message = log.get('message', '')
            if 'RAG' in message:
                error_contexts['RAG Communication'] += 1
            elif 'auth' in message.lower():
                error_contexts['Authentication'] += 1
            elif 'database' in message.lower() or 'db' in message.lower():
                error_contexts['Database'] += 1
            else:
                error_contexts['Other'] += 1
    
    return {
        'total_errors': len(errors),
        'error_types': dict(error_types.most_common(10)),
        'error_contexts': dict(error_contexts),
        'recent_errors': [
            {
                'timestamp': e['timestamp'],
                'level': e['level'],
                'message': e['message'][:200] + '...' if len(e['message']) > 200 else e['message'],
                'error_type': e.get('error_type', 'unknown')
            }
            for e in sorted(errors, key=lambda x: x['timestamp'], reverse=True)[:10]
        ]
    }


def analyze_business_events(logs: List[Dict]) -> Dict[str, Any]:
    """
    Analizar eventos de negocio.
    """
    business_events = []
    event_types = Counter()
    entity_types = Counter()
    
    for log in logs:
        if log.get('logger') == 'maverik.business':
            business_events.append(log)
            event_type = log.get('event_type', 'unknown')
            entity_type = log.get('entity_type', 'unknown')
            
            event_types[event_type] += 1
            entity_types[entity_type] += 1
    
    return {
        'total_business_events': len(business_events),
        'event_types': dict(event_types.most_common(10)),
        'entity_types': dict(entity_types),
        'recent_events': [
            {
                'timestamp': e['timestamp'],
                'event_type': e.get('event_type'),
                'entity_type': e.get('entity_type'),
                'entity_id': e.get('entity_id'),
                'user_id': e.get('user_id')
            }
            for e in sorted(business_events, key=lambda x: x['timestamp'], reverse=True)[:10]
        ]
    }


def generate_report(report_type: str, last_hours: int = None):
    """
    Generar reporte específico.
    """
    log_file = "logs/maverik_backend.log"
    logs = load_logs(log_file, last_hours)
    
    if not logs:
        print(f"❌ No se encontraron logs para analizar")
        return
    
    print(f"📊 Analizando {len(logs)} entradas de log")
    if last_hours:
        print(f"⏰ Últimas {last_hours} horas")
    print("=" * 60)
    
    if report_type == "performance":
        results = analyze_performance(logs)
        print("🚀 REPORTE DE PERFORMANCE DE ENDPOINTS")
        print("=" * 60)
        
        for endpoint, stats in sorted(results.items(), key=lambda x: x[1]['total_requests'], reverse=True):
            print(f"\n📍 {endpoint}")
            print(f"   Total requests: {stats['total_requests']}")
            print(f"   Tiempo promedio: {stats['avg_duration_ms']}ms")
            print(f"   Rango: {stats['min_duration_ms']}ms - {stats['max_duration_ms']}ms")
            print(f"   Tasa de éxito: {stats['success_rate']:.1f}%")
            print(f"   Tasa de error: {stats['error_rate']:.1f}%")
            
            if stats['error_rate'] > 5:
                print(f"   ⚠️  Alta tasa de error!")
            if stats['avg_duration_ms'] > 1000:
                print(f"   🐌 Endpoint lento!")
    
    elif report_type == "rag-performance":
        results = analyze_rag_performance(logs)
        print("🤖 REPORTE DE PERFORMANCE RAG")
        print("=" * 60)
        
        for key, value in results.items():
            if key == 'success_rate':
                print(f"Tasa de éxito: {value:.1f}%")
                if value < 90:
                    print("   ⚠️  Baja tasa de éxito del RAG!")
            elif 'time' in key:
                print(f"{key.replace('_', ' ').title()}: {value}ms")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
    
    elif report_type == "errors":
        results = analyze_errors(logs)
        print("❌ REPORTE DE ERRORES")
        print("=" * 60)
        
        print(f"Total de errores: {results['total_errors']}")
        
        print("\n🔍 Tipos de error más frecuentes:")
        for error_type, count in results['error_types'].items():
            print(f"   {error_type}: {count}")
        
        print("\n📍 Contextos de error:")
        for context, count in results['error_contexts'].items():
            print(f"   {context}: {count}")
        
        print("\n🕐 Errores recientes:")
        for error in results['recent_errors'][:5]:
            print(f"   [{error['timestamp']}] {error['level']}: {error['message']}")
    
    elif report_type == "business":
        results = analyze_business_events(logs)
        print("💼 REPORTE DE EVENTOS DE NEGOCIO")
        print("=" * 60)
        
        print(f"Total de eventos: {results['total_business_events']}")
        
        print("\n📊 Tipos de evento:")
        for event_type, count in results['event_types'].items():
            print(f"   {event_type}: {count}")
        
        print("\n🎯 Tipos de entidad:")
        for entity_type, count in results['entity_types'].items():
            print(f"   {entity_type}: {count}")
    
    else:
        print(f"❌ Tipo de reporte desconocido: {report_type}")
        print("Tipos disponibles: performance, rag-performance, errors, business")


def main():
    parser = argparse.ArgumentParser(description="Analizar logs de Maverik Backend")
    parser.add_argument(
        "--report", 
        choices=["performance", "rag-performance", "errors", "business"],
        required=True,
        help="Tipo de reporte a generar"
    )
    parser.add_argument(
        "--last-hours",
        type=int,
        help="Analizar solo las últimas N horas"
    )
    
    args = parser.parse_args()
    
    try:
        generate_report(args.report, args.last_hours)
    except KeyboardInterrupt:
        print("\n👋 Análisis cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()