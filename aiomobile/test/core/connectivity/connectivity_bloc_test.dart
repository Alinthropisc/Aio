import 'dart:async';
import 'package:bloc_test/bloc_test.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:aiomobile/core/connectivity/connectivity_bloc.dart';
import 'package:aiomobile/core/network/connectivity_service.dart';

class MockConnectivityService extends Mock implements ConnectivityService {}

void main() {
  late MockConnectivityService service;
  late StreamController<bool> controller;

  setUp(() {
    service = MockConnectivityService();
    controller = StreamController<bool>.broadcast();
    when(() => service.onConnectivityChanged).thenAnswer((_) => controller.stream);
  });

  tearDown(() => controller.close());

  test('initial state is ConnectivityUnknown', () {
    when(() => service.isConnected).thenAnswer((_) async => true);
    final bloc = ConnectivityBloc(service);
    expect(bloc.state, const ConnectivityUnknown());
    bloc.close();
  });

  blocTest<ConnectivityBloc, ConnectivityState>(
    'emits ConnectivityOnline when device is online',
    build: () {
      when(() => service.isConnected).thenAnswer((_) async => true);
      return ConnectivityBloc(service);
    },
    act: (b) => b.add(ConnectivityStartMonitoring()),
    expect: () => [const ConnectivityOnline()],
  );

  blocTest<ConnectivityBloc, ConnectivityState>(
    'emits ConnectivityOffline when device is offline',
    build: () {
      when(() => service.isConnected).thenAnswer((_) async => false);
      return ConnectivityBloc(service);
    },
    act: (b) => b.add(ConnectivityStartMonitoring()),
    expect: () => [const ConnectivityOffline()],
  );

  blocTest<ConnectivityBloc, ConnectivityState>(
    'transitions Online → Offline → Online from stream',
    build: () {
      when(() => service.isConnected).thenAnswer((_) async => true);
      return ConnectivityBloc(service);
    },
    act: (b) async {
      b.add(ConnectivityStartMonitoring());
      await Future<void>.delayed(Duration.zero);
      controller.add(false);
      await Future<void>.delayed(Duration.zero);
      controller.add(true);
    },
    expect: () => [
      const ConnectivityOnline(),
      const ConnectivityOffline(),
      const ConnectivityOnline(),
    ],
  );
}
