import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import 'package:aiomobile/core/error/exceptions.dart';
import 'package:aiomobile/core/error/failures.dart';
import 'package:aiomobile/features/auth/data/datasources/auth_remote_datasource.dart';
import 'package:aiomobile/features/auth/data/models/auth_response.dart';
import 'package:aiomobile/features/auth/data/repositories/auth_repository_impl.dart';

class MockAuthRemoteDataSource extends Mock implements AuthRemoteDataSource {}

void main() {
  late MockAuthRemoteDataSource dataSource;
  late AuthRepositoryImpl repo;

  const tEmail = 'test@aio.dev';
  const tPassword = 'pass123';
  final tResponse = AuthTokenResponse(
    accessToken: 'token',
    user: UserModel(id: '1', email: tEmail),
  );

  setUp(() {
    dataSource = MockAuthRemoteDataSource();
    repo = AuthRepositoryImpl(dataSource);
  });

  group('login', () {
    test('returns data on success', () async {
      when(() => dataSource.login(email: tEmail, password: tPassword))
          .thenAnswer((_) async => tResponse);

      final result = await repo.login(email: tEmail, password: tPassword);

      expect(result.failure, isNull);
      expect(result.data?.accessToken, 'token');
      expect(result.data?.user.email, tEmail);
    });

    test('returns ServerFailure on ServerException', () async {
      when(() => dataSource.login(email: tEmail, password: tPassword))
          .thenThrow(const ServerException('Unauthorized', statusCode: 401));

      final result = await repo.login(email: tEmail, password: tPassword);

      expect(result.data, isNull);
      expect(result.failure, isA<ServerFailure>());
      expect((result.failure as ServerFailure).statusCode, 401);
    });

    test('returns NetworkFailure on NetworkException', () async {
      when(() => dataSource.login(email: tEmail, password: tPassword))
          .thenThrow(const NetworkException('No connection'));

      final result = await repo.login(email: tEmail, password: tPassword);

      expect(result.data, isNull);
      expect(result.failure, isA<NetworkFailure>());
    });
  });
}
